from typing import Protocol, Any

class CheckpointStore(Protocol):
    async def save(self, task_id: str, checkpoint: dict[str, Any]) -> None: ...
    async def load(self, task_id: str) -> dict[str, Any] | None: ...

class InMemoryCheckpointStore:
    """Development adapter only; replace with PostgreSQL/Redis for restart recovery."""
    def __init__(self): self._items: dict[str, dict[str, Any]] = {}
    async def save(self, task_id: str, checkpoint: dict[str, Any]) -> None: self._items[task_id] = checkpoint
    async def load(self, task_id: str) -> dict[str, Any] | None: return self._items.get(task_id)
