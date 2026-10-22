from pydantic import BaseModel, Field


class AgentOptions(BaseModel):
    quality_check: bool = True
    include_execution_trace: bool = True
    max_steps: int | None = Field(default=None, ge=1, le=20)
