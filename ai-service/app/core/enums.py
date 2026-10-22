from enum import StrEnum

class AgentStatus(StrEnum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    NEEDS_REVIEW = "NEEDS_REVIEW"

class WorkflowStep(StrEnum):
    VALIDATE = "VALIDATE"
    OCR = "OCR"
    TRANSLATE = "TRANSLATE"
    INPAINT = "INPAINT"
    TYPESET = "TYPESET"
    RENDER_PREVIEW = "RENDER_PREVIEW"
    QUALITY_CHECK = "QUALITY_CHECK"
    COMPLETED = "COMPLETED"

class ToolName(StrEnum):
    OCR = "ocr"
    TRANSLATE = "translate"
    INPAINT = "inpaint"
    TYPESET = "typeset"
    RENDER_PREVIEW = "render_preview"
    QUALITY_CHECK = "quality_check"
