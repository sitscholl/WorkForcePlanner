from pydantic import BaseModel
from typing import Optional

class Field(BaseModel):
    field: str
    variety: str
    order: Optional[int] = None
