from dataclasses import dataclass, field

@dataclass
class ConversationMemory:
    """一个"有上限的对话历史容器"，用来保存最近若干轮对话消息（限 12 条），供后续喂给大语言模型（LLM）作为上下文。"""
    max_items: int = 12
    items: list[dict[str, str]] = field(default_factory=list)
    def add(self, role: str, content: str) -> None:
        self.items.append({"role": role, "content": content})
        self.items = self.items[-self.max_items:]
    def recent(self) -> list[dict[str, str]]: return list(self.items)
