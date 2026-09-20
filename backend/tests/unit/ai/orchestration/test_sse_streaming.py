"""
GrowFlow — Unit 5 Test: Real-Time SSE Event Manager & Streaming.

Tests:
- BlueprintEventManager pub/sub broadcast
- Monotonic event ID sequencing (<project_id>_<generation>_<seq>)
- Multi-subscriber isolation and delivery
- Subscriber eviction on bounded queue overflow (maxsize=100)
- Bounded replay ring buffer (50 events) and Last-Event-ID replay
- Generation isolation during replay
- Unsubscribe and cleanup
- Regeneration.started lifecycle event emission by WorkflowNodeRegistry
- Safe public projection formatting
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest

from backend.app.domain.ai.orchestration.events import (
    BlueprintEventManager,
    WorkflowEvent,
    WorkflowEventType,
)
from backend.app.domain.ai.orchestration.nodes import WorkflowNodeRegistry
from backend.app.domain.blueprint.models import BlueprintQAStatus

if TYPE_CHECKING:
    from backend.app.domain.ai.orchestration.state import OrchestrationState


@pytest.mark.asyncio
async def test_event_manager_publish_subscribe_delivery() -> None:
    manager = BlueprintEventManager()
    project_id = "proj-101"

    queue = await manager.subscribe(project_id)
    assert manager.get_subscriber_count(project_id) == 1

    event = WorkflowEvent(
        event_type=WorkflowEventType.JOB_STARTED.value,
        job_id="job-1",
        project_id=project_id,
        generation_number=1,
        step="idea",
        progress_percent=5,
    )

    await manager.publish(event)

    received = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert received.event_type == WorkflowEventType.JOB_STARTED.value
    assert received.event_id == "proj-101_1_001"
    assert received.job_id == "job-1"
    assert received.generation_number == 1


@pytest.mark.asyncio
async def test_event_manager_monotonic_event_ids() -> None:
    manager = BlueprintEventManager()
    project_id = "proj-102"
    queue = await manager.subscribe(project_id)

    for i in range(1, 6):
        await manager.publish(
            WorkflowEvent(
                event_type=WorkflowEventType.NODE_STARTED.value,
                job_id="job-2",
                project_id=project_id,
                generation_number=2,
                step=f"step_{i}",
            )
        )

    for i in range(1, 6):
        rec = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert rec.event_id == f"proj-102_2_{i:03d}"


@pytest.mark.asyncio
async def test_event_manager_project_isolation() -> None:
    manager = BlueprintEventManager()
    proj_a = "proj-aaa"
    proj_b = "proj-bbb"

    queue_a = await manager.subscribe(proj_a)
    queue_b = await manager.subscribe(proj_b)

    # Publish to A
    await manager.publish(
        WorkflowEvent(
            event_type=WorkflowEventType.NODE_STARTED.value,
            job_id="job-a",
            project_id=proj_a,
            generation_number=1,
            step="idea",
        )
    )

    # A receives it
    rec_a = await asyncio.wait_for(queue_a.get(), timeout=1.0)
    assert rec_a.project_id == proj_a

    # B must NOT receive it
    assert queue_b.empty()


@pytest.mark.asyncio
async def test_event_manager_multi_subscribers() -> None:
    manager = BlueprintEventManager()
    project_id = "proj-multi"

    queue1 = await manager.subscribe(project_id)
    queue2 = await manager.subscribe(project_id)
    assert manager.get_subscriber_count(project_id) == 2

    await manager.publish(
        WorkflowEvent(
            event_type=WorkflowEventType.NODE_COMPLETED.value,
            job_id="job-m",
            project_id=project_id,
            generation_number=1,
            step="technology",
            progress_percent=30,
        )
    )

    rec1 = await asyncio.wait_for(queue1.get(), timeout=1.0)
    rec2 = await asyncio.wait_for(queue2.get(), timeout=1.0)

    assert rec1.event_id == rec2.event_id
    assert rec1.step == "technology"
    assert rec2.step == "technology"

    # Unsubscribe one
    await manager.unsubscribe(project_id, queue1)
    assert manager.get_subscriber_count(project_id) == 1

    # Publish another
    await manager.publish(
        WorkflowEvent(
            event_type=WorkflowEventType.NODE_STARTED.value,
            job_id="job-m",
            project_id=project_id,
            generation_number=1,
            step="specification",
        )
    )

    # Only queue2 receives it
    rec2_next = await asyncio.wait_for(queue2.get(), timeout=1.0)
    assert rec2_next.step == "specification"
    assert queue1.empty()


@pytest.mark.asyncio
async def test_event_manager_subscriber_eviction_on_overflow() -> None:
    # Set queue maxsize to 2
    manager = BlueprintEventManager(queue_maxsize=2)
    project_id = "proj-overflow"

    _ = await manager.subscribe(project_id)
    assert manager.get_subscriber_count(project_id) == 1

    # Fill queue to capacity (2 items)
    await manager.publish(
        WorkflowEvent(
            event_type=WorkflowEventType.NODE_STARTED.value,
            job_id="job-1",
            project_id=project_id,
            generation_number=1,
            step="step1",
        )
    )
    await manager.publish(
        WorkflowEvent(
            event_type=WorkflowEventType.NODE_STARTED.value,
            job_id="job-1",
            project_id=project_id,
            generation_number=1,
            step="step2",
        )
    )

    # 3rd publish overflows the queue; slow_queue must be evicted immediately without blocking
    await manager.publish(
        WorkflowEvent(
            event_type=WorkflowEventType.NODE_STARTED.value,
            job_id="job-1",
            project_id=project_id,
            generation_number=1,
            step="step3",
        )
    )

    # Subscriber count must now be 0 (evicted)
    assert manager.get_subscriber_count(project_id) == 0


@pytest.mark.asyncio
async def test_event_manager_replay_buffer_bounded() -> None:
    # Buffer capacity = 5
    manager = BlueprintEventManager(replay_buffer_size=5)
    project_id = "proj-replay-bound"

    for i in range(1, 10):
        await manager.publish(
            WorkflowEvent(
                event_type=WorkflowEventType.NODE_STARTED.value,
                job_id="job-b",
                project_id=project_id,
                generation_number=1,
                step=f"step_{i}",
            )
        )

    # Only the last 5 events remain (steps 5, 6, 7, 8, 9)
    # Event IDs: ..._005, ..._006, ..._007, ..._008, ..._009
    replayed = manager.get_replay_events(project_id, f"{project_id}_1_006")
    assert len(replayed) == 3
    assert [e.event_id for e in replayed] == [
        f"{project_id}_1_007",
        f"{project_id}_1_008",
        f"{project_id}_1_009",
    ]

    # Stale ID that has been evicted
    evicted_replayed = manager.get_replay_events(project_id, f"{project_id}_1_002")
    assert evicted_replayed == []


@pytest.mark.asyncio
async def test_event_manager_replay_generation_isolation() -> None:
    manager = BlueprintEventManager(replay_buffer_size=10)
    project_id = "proj-gen-iso"

    # Generation 1 event
    await manager.publish(
        WorkflowEvent(
            event_type=WorkflowEventType.JOB_COMPLETED.value,
            job_id="job-g1",
            project_id=project_id,
            generation_number=1,
            step="completed",
        )
    )

    # Generation 2 events
    await manager.publish(
        WorkflowEvent(
            event_type=WorkflowEventType.JOB_STARTED.value,
            job_id="job-g2",
            project_id=project_id,
            generation_number=2,
            step="idea",
        )
    )
    await manager.publish(
        WorkflowEvent(
            event_type=WorkflowEventType.NODE_STARTED.value,
            job_id="job-g2",
            project_id=project_id,
            generation_number=2,
            step="scope",
        )
    )

    # Requesting replay for Generation 1 must NOT return Generation 2 events
    gen1_replay = manager.get_replay_events(project_id, f"{project_id}_1_001")
    assert gen1_replay == []

    # Requesting replay for Generation 2 event 1 returns event 2
    gen2_replay = manager.get_replay_events(project_id, f"{project_id}_2_001")
    assert len(gen2_replay) == 1
    assert gen2_replay[0].event_id == f"{project_id}_2_002"


@pytest.mark.asyncio
async def test_event_manager_replay_stale_or_invalid_id() -> None:
    manager = BlueprintEventManager()
    project_id = "proj-invalid"

    await manager.publish(
        WorkflowEvent(
            event_type=WorkflowEventType.JOB_STARTED.value,
            job_id="job-1",
            project_id=project_id,
            generation_number=1,
        )
    )

    assert manager.get_replay_events(project_id, None) == []
    assert manager.get_replay_events(project_id, "") == []
    assert manager.get_replay_events(project_id, "invalid_id_format") == []
    assert manager.get_replay_events(project_id, "other_proj_1_001") == []
    assert manager.get_replay_events(project_id, f"{project_id}_notnum_001") == []
    assert manager.get_replay_events(project_id, f"{project_id}_1_999") == []


@pytest.mark.asyncio
async def test_workflow_node_registry_emits_regeneration_started() -> None:
    """Verify that node_regeneration_router in WorkflowNodeRegistry dispatches regeneration.started."""
    event_publisher = AsyncMock()
    registry = WorkflowNodeRegistry(
        gateway=MagicMock(),
        event_publisher=event_publisher,
    )

    state: OrchestrationState = {
        "project_id": str(uuid.uuid4()),
        "student_id": str(uuid.uuid4()),
        "execution_id": "exec-regen-test",
        "correlation_id": "corr-regen-test",
        "generation_number": 1,
        "current_step": "qa_judge",
        "workflow_status": "RUNNING",
        "regeneration_attempt": 0,
        "qa_score": 60,
        "qa_status": BlueprintQAStatus.FAIL,
        "qa_findings": [
            {
                "target_agent": "timeline",
                "requires_regeneration": True,
                "severity": "CRITICAL",
                "recommendation": "Extend milestone deadlines.",
            }
        ],
    }

    result = await registry.node_regeneration_router(state)

    assert result["regeneration_attempt"] == 1
    assert result["regeneration_target"] == "timeline"
    assert "regenerating_timeline" in result["current_step"]

    # Check that event_publisher.publish was called with regeneration.started
    assert event_publisher.publish.called
    published_event: WorkflowEvent = event_publisher.publish.call_args[0][0]
    assert published_event.event_type == WorkflowEventType.REGENERATION_STARTED.value
    assert published_event.payload["regeneration_attempt"] == 1
    assert published_event.payload["regeneration_target"] == "timeline"
    assert published_event.payload["qa_feedback_hint"] == "Extend milestone deadlines."
