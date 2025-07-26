from pydantic import BaseModel
from typing import Optional

class Field(BaseModel):
    field: str
    variety: str
    harvest_round: int = 1
    order: Optional[int] = None
