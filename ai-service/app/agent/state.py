from dataclasses import dataclass, field
from app.core.enums import *
from app.api.schemas.response import AgentTraceItem

@dataclass
class AgentState:
    status: AgentStatus = AgentStatus.CREATED
    current_step: WorkflowStep = WorkflowStep.VALIDATE
    completed_steps: list[WorkflowStep] = field(default_factory=list)
    trace: list[AgentTraceItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    step_count: int = 0

    def enter(self, step: WorkflowStep) -> None:
        self.current_step = step
        self.step_count += 1

    def complete(self, step: WorkflowStep) -> None:
        if step not in self.completed_steps:
            self.completed_steps.append(step)
