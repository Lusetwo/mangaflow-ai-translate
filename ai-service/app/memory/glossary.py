class Glossary:
    """一个"术语表"（词汇对照表）的内存适配器，用于保存和查询"源词 → 译词"的映射，比如把日文专有名词映射到固定的中文译法，保证翻译一致性。"""
    def __init__(self, terms: dict[str, str] | None = None):
        self._terms = terms or {}
    def lookup(self, term: str) -> str | None:
        return self._terms.get(term)
    def add(self, source: str, target: str) -> None:
        self._terms[source] = target
