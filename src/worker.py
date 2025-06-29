from pydantic import BaseModel, Field, ConfigDict

from .workforce import Workforce

class Worker(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    work_hours: int
    work_days: list[str]
    workforce: Workforce
    payment: int | None = Field(default = None)

    def model_post_init(self, __context):
        """Called after model initialization - Pydantic equivalent of __post_init__"""
        self.workforce.add_worker(self)