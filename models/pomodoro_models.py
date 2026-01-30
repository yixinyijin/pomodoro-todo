"""
Pomodoro data models.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Pomodoro:
    """Pomodoro session data model."""
    id: int
    task_id: Optional[int]
    duration: int  # Duration in seconds
    start_time: str
    end_time: str

    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes."""
        return self.duration / 60
