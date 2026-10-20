class MangaFlowError(Exception):
    """Base exception safe to map to an API response."""

class ConfigurationError(MangaFlowError):
    pass

class ToolNotFoundError(MangaFlowError):
    pass

class ToolExecutionError(MangaFlowError):
    pass

class ProviderError(MangaFlowError):
    pass
