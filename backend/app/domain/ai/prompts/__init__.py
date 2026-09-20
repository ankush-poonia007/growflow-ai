"""
GrowFlow — Domain AI Prompts Package.

Exports prompt version constants and prompt construction helpers for all 12 agents.
"""

from __future__ import annotations

from backend.app.domain.ai.prompts.features import (
    PROMPT_VERSION as FEATURES_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.features import (
    build_features_system_prompt,
    build_features_user_prompt,
)
from backend.app.domain.ai.prompts.idea import (
    PROMPT_VERSION as IDEA_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.idea import (
    build_idea_system_prompt,
    build_idea_user_prompt,
)
from backend.app.domain.ai.prompts.milestone import (
    PROMPT_VERSION as MILESTONE_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.milestone import (
    build_milestone_system_prompt,
    build_milestone_user_prompt,
)
from backend.app.domain.ai.prompts.mvp import (
    PROMPT_VERSION as MVP_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.mvp import (
    build_mvp_system_prompt,
    build_mvp_user_prompt,
)
from backend.app.domain.ai.prompts.qa import (
    PROMPT_VERSION as QA_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.qa import (
    build_qa_judge_system_prompt,
    build_qa_judge_user_prompt,
)
from backend.app.domain.ai.prompts.readme import (
    PROMPT_VERSION as README_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.readme import (
    build_readme_system_prompt,
    build_readme_user_prompt,
)
from backend.app.domain.ai.prompts.risk import (
    PROMPT_VERSION as RISK_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.risk import (
    build_risk_system_prompt,
    build_risk_user_prompt,
)
from backend.app.domain.ai.prompts.scope import (
    PROMPT_VERSION as SCOPE_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.scope import (
    build_scope_system_prompt,
    build_scope_user_prompt,
)
from backend.app.domain.ai.prompts.specification import (
    PROMPT_VERSION as SPECIFICATION_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.specification import (
    build_specification_system_prompt,
    build_specification_user_prompt,
)
from backend.app.domain.ai.prompts.system import SHARED_SYSTEM_PROMPT
from backend.app.domain.ai.prompts.task import (
    PROMPT_VERSION as TASK_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.task import (
    build_task_system_prompt,
    build_task_user_prompt,
)
from backend.app.domain.ai.prompts.technology import (
    PROMPT_VERSION as TECHNOLOGY_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.technology import (
    build_technology_system_prompt,
    build_technology_user_prompt,
)
from backend.app.domain.ai.prompts.timeline import (
    PROMPT_VERSION as TIMELINE_PROMPT_VERSION,
)
from backend.app.domain.ai.prompts.timeline import (
    build_timeline_system_prompt,
    build_timeline_user_prompt,
)

__all__ = [
    "FEATURES_PROMPT_VERSION",
    "IDEA_PROMPT_VERSION",
    "MILESTONE_PROMPT_VERSION",
    "MVP_PROMPT_VERSION",
    "QA_PROMPT_VERSION",
    "README_PROMPT_VERSION",
    "RISK_PROMPT_VERSION",
    "SCOPE_PROMPT_VERSION",
    "SHARED_SYSTEM_PROMPT",
    "SPECIFICATION_PROMPT_VERSION",
    "TASK_PROMPT_VERSION",
    "TECHNOLOGY_PROMPT_VERSION",
    "TIMELINE_PROMPT_VERSION",
    "build_features_system_prompt",
    "build_features_user_prompt",
    "build_idea_system_prompt",
    "build_idea_user_prompt",
    "build_milestone_system_prompt",
    "build_milestone_user_prompt",
    "build_mvp_system_prompt",
    "build_mvp_user_prompt",
    "build_qa_judge_system_prompt",
    "build_qa_judge_user_prompt",
    "build_readme_system_prompt",
    "build_readme_user_prompt",
    "build_risk_system_prompt",
    "build_risk_user_prompt",
    "build_scope_system_prompt",
    "build_scope_user_prompt",
    "build_specification_system_prompt",
    "build_specification_user_prompt",
    "build_task_system_prompt",
    "build_task_user_prompt",
    "build_technology_system_prompt",
    "build_technology_user_prompt",
    "build_timeline_system_prompt",
    "build_timeline_user_prompt",
]
