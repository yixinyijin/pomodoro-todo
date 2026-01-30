"""
Todo list management module.
"""
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    """Task data model."""
    id: int
    title: str
    description: str = ""
    priority: int = 2  # 1: High, 2: Medium, 3: Low
    status: int = 0  # 0: Pending, 1: In Progress, 2: Completed
    created_at: str = ""
    updated_at: str = ""

    @property
    def priority_label(self) -> str:
        """Get priority label."""
        labels = {1: "High", 2: "Medium", 3: "Low"}
        return labels.get(self.priority, "Medium")

    @property
    def status_label(self) -> str:
        """Get status label."""
        labels = {0: "Pending", 1: "In Progress", 2: "Completed"}
        return labels.get(self.status, "Pending")


class TaskManager:
    """Task management class."""

    def __init__(self, db):
        """
        Initialize task manager.

        Args:
            db: Database instance
        """
        self.db = db

    def create_task(self, title: str, description: str = "", priority: int = 2) -> Task:
        """Create a new task."""
        task_id = self.db.create_task(title, description, priority)
        task_data = self.db.get_task(task_id)
        return Task(**task_data)

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get task by ID."""
        task_data = self.db.get_task(task_id)
        return Task(**task_data) if task_data else None

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        tasks_data = self.db.get_all_tasks()
        return [Task(**t) for t in tasks_data]

    def get_tasks_by_status(self, status: int) -> List[Task]:
        """Get tasks by status."""
        tasks_data = self.db.get_tasks_by_status(status)
        return [Task(**t) for t in tasks_data]

    def update_task(self, task_id: int, **kwargs):
        """Update task fields."""
        self.db.update_task(task_id, **kwargs)

    def delete_task(self, task_id: int):
        """Delete task."""
        self.db.delete_task(task_id)

    def mark_in_progress(self, task_id: int):
        """Mark task as in progress."""
        self.update_task(task_id, status=1)

    def mark_completed(self, task_id: int):
        """Mark task as completed."""
        self.update_task(task_id, status=2)

    def set_priority(self, task_id: int, priority: int):
        """Set task priority."""
        self.update_task(task_id, priority=priority)
