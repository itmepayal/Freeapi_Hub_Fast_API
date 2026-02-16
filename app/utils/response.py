# =====================================
# Typing Imports
# =====================================
from typing import Generic, TypeVar, Optional, Dict, Any

# =====================================
# Pydantic Imports
# =====================================
from pydantic import BaseModel
from pydantic.generics import GenericModel

# =====================================
# Generic Type Variable
# =====================================
T = TypeVar("T")

# =====================================
# Standard API Response Wrapper
# =====================================
class APIResponse(GenericModel, Generic[T]):
    status: str = "success"
    message: str
    data: T | None = None
    meta: Optional[Dict[str, Any]] = None
