from pydantic import BaseModel, Field, ConfigDict, model_validator

import datetime

# from .workforce import Workforce

class Worker(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    work_hours: float
    work_days: list[str]
    payment: float | None = Field(default = None)

    @model_validator(mode = 'after')
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        return self

    def get_daily_work_hours(self, date):
        if self.start_date.date() <= date <= self.end_date.date():
            return self.work_hours
        return 0

