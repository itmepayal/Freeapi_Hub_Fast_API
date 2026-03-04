# =====================================
# Standard Library
# =====================================
from enum import Enum

# =====================================
# TodoStatus Enum
# =====================================
class TodoStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

# =====================================
# TodoPriority Enum
# =====================================
class TodoPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
