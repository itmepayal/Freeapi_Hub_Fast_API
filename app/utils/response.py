# =====================================
# Typing
# =====================================
from typing import Generic, TypeVar, Optional, Dict, Any

# =====================================
# Pydantic
# =====================================
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


# =====================================
# Standard API Response Wrapper
# =====================================
class APIResponse(BaseModel, Generic[T]):
    status: str = "success"
    message: str
    data: Optional[T] = None
    meta: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )