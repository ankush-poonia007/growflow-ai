"""
GrowFlow — Unit 4 Internal Event Boundary for Orchestration & Unit 5 Integration.

Defines lifecycle events emitted during graph execution:
- job.started
- node.started
- node.completed
- qa.evaluated
- regeneration.started
- job.completed
- job.failed
- job.cancelled

No SSE, streaming, or frontend listeners are implemented here (Unit 5 boundary).
"""

from __future__ import annotations

import asyncio
from collections import deque
import dataclasses
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
import logging
from typing import Any, Protocol

logger = logging.getLogger("growflow.ai.orchestration.events")


class WorkflowEventType(StrEnum):
    JOB_STARTED = "job.started"
    NODE_STARTED = "node.started"
    NODE_COMPLETED = "node.completed"
    QA_EVALUATED = "qa.evaluated"
    REGENERATION_STARTED = "regeneration.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    JOB_CANCELLED = "job.cancelled"


@dataclass(frozen=True)
class WorkflowEvent:
    event_type: str
    job_id: str
    project_id: str
    generation_number: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    step: str | None = None
    progress_percent: int | None = None
    execution_id: str | None = None
    correlation_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str | None = None


class WorkflowEventPublisher(Protocol):
    async def publish(self, event: WorkflowEvent) -> None:
        """Publish a workflow lifecycle event asynchronously."""
        ...


class NoOpEventPublisher:
    """Default no-op publisher when no external subscribers are registered."""

    async def publish(self, event: WorkflowEvent) -> None:
        pass


class InMemoryEventPublisher:
    """In-memory event publisher useful for testing and Unit 5 event capture."""

    def __init__(self) -> None:
        self.events: list[WorkflowEvent] = []

    async def publish(self, event: WorkflowEvent) -> None:
        self.events.append(event)

    def clear(self) -> None:
        self.events.clear()


class BlueprintEventManager:
    """
    In-process, non-blocking pub/sub broadcast manager for blueprint generation events.

    Provides:
    - Bounded per-subscriber asyncio.Queue instances (maxsize=100)
    - Non-blocking event publication (put_nowait); slow clients are evicted to protect the worker
    - Bounded in-memory ring buffer (default 50 events) per active project for Last-Event-ID replay
    - Monotonic event IDs formatted as <project_id>_<generation_number>_<sequence:03d>
    - Project-scoped subscriber isolation
    """

    def __init__(self, replay_buffer_size: int = 50, queue_maxsize: int = 100) -> None:
        self._replay_buffer_size = replay_buffer_size
        self._queue_maxsize = queue_maxsize
        self._subscribers: dict[str, set[asyncio.Queue[WorkflowEvent]]] = {}
        self._replay_buffers: dict[str, deque[WorkflowEvent]] = {}
        self._sequences: dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def publish(self, event: WorkflowEvent) -> None:
        """
        Publish an event to all active subscribers for the project.
        Assigns monotonic event_id, records into replay ring buffer, and delivers non-blockingly.
        """
        proj_id = str(event.project_id)
        gen = event.generation_number

        # 1. Assign monotonic sequence and event_id if not present
        seq_key = f"{proj_id}_{gen}"
        seq = self._sequences.get(seq_key, 0) + 1
        self._sequences[seq_key] = seq
        event_id = event.event_id or f"{proj_id}_{gen}_{seq:03d}"
        event_to_dispatch = (
            dataclasses.replace(event, event_id=event_id) if event.event_id is None else event
        )

        # 2. Record in bounded replay buffer
        if proj_id not in self._replay_buffers:
            self._replay_buffers[proj_id] = deque(maxlen=self._replay_buffer_size)
        self._replay_buffers[proj_id].append(event_to_dispatch)

        # 3. Non-blocking dispatch to subscriber queues
        subscriber_set = self._subscribers.get(proj_id)
        if not subscriber_set:
            return

        evicted: list[asyncio.Queue[WorkflowEvent]] = []
        for q in list(subscriber_set):
            try:
                q.put_nowait(event_to_dispatch)
            except asyncio.QueueFull:
                evicted.append(q)
                logger.warning(
                    "Evicted slow subscriber queue due to buffer overflow",
                    extra={"project_id": proj_id, "event_id": event_id},
                )

        if evicted:
            async with self._lock:
                for q in evicted:
                    self._subscribers.get(proj_id, set()).discard(q)

    async def subscribe(self, project_id: str) -> asyncio.Queue[WorkflowEvent]:
        """Create and register a new bounded subscriber queue for a project."""
        proj_id = str(project_id)
        q: asyncio.Queue[WorkflowEvent] = asyncio.Queue(maxsize=self._queue_maxsize)
        async with self._lock:
            if proj_id not in self._subscribers:
                self._subscribers[proj_id] = set()
            self._subscribers[proj_id].add(q)
        return q

    async def unsubscribe(self, project_id: str, queue: asyncio.Queue[WorkflowEvent]) -> None:
        """Unregister a subscriber queue and clean up empty project subscriber sets."""
        proj_id = str(project_id)
        async with self._lock:
            if proj_id in self._subscribers:
                self._subscribers[proj_id].discard(queue)
                if not self._subscribers[proj_id]:
                    del self._subscribers[proj_id]

    def get_replay_events(self, project_id: str, last_event_id: str | None) -> list[WorkflowEvent]:
        """
        Retrieve events from the replay buffer published strictly after last_event_id.
        Returns an empty list if last_event_id is None, malformed, or evicted from the buffer.
        """
        if not last_event_id:
            return []

        proj_id = str(project_id)
        buffer = self._replay_buffers.get(proj_id)
        if not buffer:
            return []

        # Validate last_event_id belongs to the requested project
        parts = last_event_id.rsplit("_", 2)
        if len(parts) != 3 or parts[0] != proj_id:
            return []

        try:
            req_gen = int(parts[1])
        except ValueError:
            return []

        found = False
        replayed: list[WorkflowEvent] = []
        for ev in buffer:
            if found:
                # Generation isolation: do not replay events across generation boundaries
                if ev.generation_number == req_gen:
                    replayed.append(ev)
            elif ev.event_id == last_event_id:
                found = True

        return replayed if found else []

    def get_subscriber_count(self, project_id: str) -> int:
        """Return the number of active subscribers for a project."""
        return len(self._subscribers.get(str(project_id), set()))

    def clear_project(self, project_id: str) -> None:
        """Clear subscribers, replay buffer, and sequence tracking for a specific project."""
        proj_id = str(project_id)
        self._subscribers.pop(proj_id, None)
        self._replay_buffers.pop(proj_id, None)
        keys_to_remove = [k for k in self._sequences if k.startswith(f"{proj_id}_")]
        for k in keys_to_remove:
            self._sequences.pop(k, None)

    def clear_all(self) -> None:
        """Clear all active subscribers, buffers, and sequence counters across all projects."""
        self._subscribers.clear()
        self._replay_buffers.clear()
        self._sequences.clear()


_default_event_manager: BlueprintEventManager | None = None


def get_blueprint_event_manager() -> BlueprintEventManager:
    """Return the application-level shared BlueprintEventManager singleton."""
    global _default_event_manager
    if _default_event_manager is None:
        _default_event_manager = BlueprintEventManager()
    return _default_event_manager


def set_blueprint_event_manager(manager: BlueprintEventManager | None) -> None:
    """Explicitly set or reset the shared BlueprintEventManager singleton (primarily for testing)."""
    global _default_event_manager
    _default_event_manager = manager
