"""
Todo list data models.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class TodoTask:
    """Todo task data model."""
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
        labels = {1: "高", 2: "中", 3: "低"}
        return labels.get(self.priority, "中")

    @property
    def status_label(self) -> str:
        """Get status label."""
        labels = {0: "待办", 1: "进行中", 2: "已完成"}
        return labels.get(self.status, "待办")
