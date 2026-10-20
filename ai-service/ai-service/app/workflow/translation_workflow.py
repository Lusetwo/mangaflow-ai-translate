from app.agent.context import AgentContext
from app.agent.manga_agent import MangaAgent
from app.workflow.checkpoint import InMemoryCheckpointStore

class TranslationWorkflow:
    def __init__(self, agent: MangaAgent | None = None, checkpoint_store=None):
        self.agent = agent or MangaAgent()
        self.checkpoint_store = checkpoint_store or InMemoryCheckpointStore()
    async def execute(self, context: AgentContext) -> AgentContext:
        await self.checkpoint_store.save(context.task_id, {"status": "RUNNING", "step": "STARTED"})
        result = await self.agent.run(context)
        await self.checkpoint_store.save(context.task_id, {"status": result.state.status.value,
            "completed_steps": [s.value for s in result.state.completed_steps],
            "quality_report": result.quality_report})
        return result