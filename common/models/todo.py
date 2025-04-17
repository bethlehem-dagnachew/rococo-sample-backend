from dataclasses import dataclass, field
from datetime import datetime

from rococo.models.versioned_model import VersionedModel, default_datetime

@dataclass
class Todo(VersionedModel):
   
    person_id: str = None
    title: str = None
    is_completed: bool = False
    created_on: datetime = field(default_factory=default_datetime)
