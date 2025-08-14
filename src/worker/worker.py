from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional
import datetime

class WorkPeriod(BaseModel):
    """Represents a work period with specific hours, days, and date range"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    start_date: datetime.datetime
    end_date: datetime.datetime
    work_hours: float
    work_days: List[str]
    
    @model_validator(mode='after')
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError("Work period start date must be before end date")
        return self
    
    def get_work_hours_for_date(self, date: datetime.date) -> float:
        """Get work hours for a specific date if it falls within this period"""
        if self.start_date.date() <= date <= self.end_date.date():
            # Check if the day of the week is a working day
            day_name = date.strftime("%A")
            if day_name in self.work_days:
                return self.work_hours
        return 0

class Worker(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    work_periods: List[WorkPeriod] = Field(default_factory=list)
    payment: Optional[float] = Field(default=None)
        
    def get_daily_work_hours(self, date: datetime.date) -> float:
        """Calculate work hours for a specific date based on work periods"""
        # Find the work period that covers this date
        for period in self.work_periods:
            hours = period.get_work_hours_for_date(date)
            if hours > 0:
                return hours
        
        return 0
    
    def add_work_period(self, work_period: WorkPeriod):
        """Add a new work period to the worker"""
        self.work_periods.append(work_period)
        # Sort periods by start date for easier management
        self.work_periods.sort(key=lambda p: p.start_date)
    
    def remove_work_period(self, index: int):
        """Remove a work period by index"""
        if 0 <= index < len(self.work_periods):
            self.work_periods.pop(index)
    
    def get_work_periods_summary(self) -> str:
        """Get a summary of all work periods for display"""
        if not self.work_periods:
            return "No work periods defined"
        
        summaries = []
        for i, period in enumerate(self.work_periods):
            start_str = period.start_date.strftime("%Y-%m-%d")
            end_str = period.end_date.strftime("%Y-%m-%d")
            days_str = ", ".join(period.work_days)
            summaries.append(f"Period {i+1}: {start_str} to {end_str}, {period.work_hours}h/day on {days_str}")
        
        return "\n".join(summaries)
    
    def get_employment_date_range(self) -> tuple[datetime.date, datetime.date]:
        """Get the overall employment date range based on work periods"""
        if not self.work_periods:
            return None, None
        
        start_dates = [period.start_date.date() for period in self.work_periods]
        end_dates = [period.end_date.date() for period in self.work_periods]
        
        return min(start_dates), max(end_dates)