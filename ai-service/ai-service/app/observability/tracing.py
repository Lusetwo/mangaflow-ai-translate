from contextvars import ContextVar
import uuid

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
def new_request_id() -> str:
    value = str(uuid.uuid4())
    request_id_var.set(value)
    return value
