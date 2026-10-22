
import dataclasses
from dataclasses import field
from typing import Any

from app.agent.state import AgentState


@dataclasses.dataclass
class AgentContext:
    """Agent 当前任务的上下文，保存输入、处理中间结果和最终输出。"""

    task_id: str
    image_bytes: bytes
    source_lang: str
    target_lang: str

    options: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    regions: list[dict[str, Any]] = field(default_factory=list)
    translations: list[str] = field(default_factory=list)

    cleaned_image_bytes: bytes | None = None
    result_image_bytes: bytes | None = None
    quality_report: dict[str, Any] = field(default_factory=dict)

    state: AgentState = field(default_factory=AgentState)
