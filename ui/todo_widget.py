"""
Compact and clean styles for Todo list widget.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QLabel, QPushButton, QLineEdit,
                             QComboBox, QMessageBox, QInputDialog, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QSize

from core.todo_manager import TaskManager, Task


class TodoWidget(QWidget):
    """Compact Todo list widget."""

    # Signals
    task_selected = pyqtSignal(int)
    task_changed = pyqtSignal()

    def __init__(self, db=None, parent=None):
        """Initialize todo widget."""
        super().__init__(parent)
        self.db = db
        self.task_manager = TaskManager(db) if db else None
        self.current_task_id = None
        self._init_ui()
        self._load_tasks()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("待办事项")
        title_label.setObjectName("sectionTitle")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Filter
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "待办", "进行中", "已完成"])
        self.filter_combo.setFixedWidth(80)
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        header_layout.addWidget(self.filter_combo)

        layout.addLayout(header_layout)

        # Task list
        self.task_list = QListWidget()
        self.task_list.setObjectName("taskList")
        self.task_list.setSpacing(2)
        self.task_list.itemClicked.connect(self._on_task_clicked)
        self.task_list.itemDoubleClicked.connect(self._on_task_double_clicked)
        layout.addWidget(self.task_list)

        # Add task row - compact
        add_layout = QHBoxLayout()
        add_layout.setSpacing(6)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("添加任务...")
        self.title_input.setFixedHeight(32)
        self.title_input.returnPressed.connect(self._on_add_task)
        add_layout.addWidget(self.title_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["高", "中", "低"])
        self.priority_combo.setFixedWidth(55)
        self.priority_combo.setCurrentIndex(1)
        add_layout.addWidget(self.priority_combo)

        self.add_button = QPushButton("添加")
        self.add_button.setObjectName("addButton")
        self.add_button.setProperty("class", "primary")
        self.add_button.setFixedSize(50, 32)
        self.add_button.clicked.connect(self._on_add_task)
        add_layout.addWidget(self.add_button)

        layout.addLayout(add_layout)

        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(6)

        self.start_button = QPushButton("开始任务")
        self.start_button.setObjectName("startButton")
        self.start_button.setProperty("class", "success")
        self.start_button.setFixedSize(70, 28)
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self._on_start_task)
        action_layout.addWidget(self.start_button)

        self.complete_button = QPushButton("完成任务")
        self.complete_button.setObjectName("completeButton")
        self.complete_button.setFixedSize(70, 28)
        self.complete_button.setEnabled(False)
        self.complete_button.clicked.connect(self._on_complete_task)
        action_layout.addWidget(self.complete_button)

        self.delete_button = QPushButton("删除")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.setFixedSize(50, 28)
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self._on_delete_task)
        action_layout.addWidget(self.delete_button)

        action_layout.addStretch()

        # Task count on right
        self.task_count_label = QLabel("0 个任务")
        self.task_count_label.setObjectName("taskCount")
        action_layout.addWidget(self.task_count_label)

        layout.addLayout(action_layout)

    def _load_tasks(self):
        """Load tasks from database."""
        self.task_list.clear()

        filter_text = self.filter_combo.currentText()
        status_map = {"全部": None, "待办": 0, "进行中": 1, "已完成": 2}
        filter_status = status_map.get(filter_text)

        if filter_status is None:
            tasks = self.task_manager.get_all_tasks() if self.task_manager else []
        else:
            tasks = self.task_manager.get_tasks_by_status(filter_status) if self.task_manager else []

        # Update task count
        self.task_count_label.setText(f"{len(tasks)} 个任务")

        for task in tasks:
            self._add_task_item(task)

    def _add_task_item(self, task: Task):
        """Add a task to the list."""
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, task.id)

        # Create widget for item
        widget = QFrame()
        widget.setObjectName("taskItem")
        widget.setFixedHeight(80)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(4)

        # Title
        title_label = QLabel(task.title)
        title_label.setObjectName("taskTitle")
        title_label.setWordWrap(True)
        top_layout = QHBoxLayout()
        top_layout.addWidget(title_label)
        top_layout.addStretch()

        # Priority
        priority_class = {1: "priority-high", 2: "priority-medium", 3: "priority-low"}
        priority_label = QLabel(task.priority_label)
        priority_label.setProperty("class", priority_class.get(task.priority, "priority-medium"))
        top_layout.addWidget(priority_label)
        layout.addLayout(top_layout)

        # Status
        status_class = {0: "status-pending", 1: "status-progress", 2: "status-completed"}
        status_label = QLabel(task.status_label)
        status_label.setProperty("class", f"status-badge {status_class.get(task.status, 'status-pending')}")
        layout.addWidget(status_label)

        item.setSizeHint(QSize(0, 80))
        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, widget)

    def _on_filter_changed(self):
        """Handle filter change."""
        self._load_tasks()

    def _on_task_clicked(self, item):
        """Handle task click."""
        task_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_task_id = task_id
        self.task_selected.emit(task_id)

        task = self.task_manager.get_task(task_id) if self.task_manager else None
        if task:
            self.start_button.setEnabled(task.status != 2)
            self.complete_button.setEnabled(task.status != 2)
            self.delete_button.setEnabled(True)

    def _on_task_double_clicked(self, item):
        """Handle task double click for editing."""
        task_id = item.data(Qt.ItemDataRole.UserRole)
        task = self.task_manager.get_task(task_id) if self.task_manager else None
        if task:
            new_title, ok = QInputDialog.getText(
                self, "编辑任务", "任务标题:", QLineEdit.EchoMode.Normal, task.title
            )
            if ok and new_title.strip():
                self.task_manager.update_task(task.id, title=new_title.strip())
                self._load_tasks()
                self.task_changed.emit()

    def _on_add_task(self):
        """Handle add task."""
        title = self.title_input.text().strip()
        if not title:
            return

        priority = self.priority_combo.currentIndex() + 1

        if self.task_manager:
            self.task_manager.create_task(title, priority=priority)
            self.title_input.clear()
            self._load_tasks()
            self.task_changed.emit()

    def _on_start_task(self):
        """Handle start task button."""
        if self.current_task_id is not None:
            self.task_manager.mark_in_progress(self.current_task_id)
            self._load_tasks()
            self.task_changed.emit()

    def _on_complete_task(self):
        """Handle complete task button."""
        if self.current_task_id is not None:
            self.task_manager.mark_completed(self.current_task_id)
            self._load_tasks()
            self.task_changed.emit()

    def _on_delete_task(self):
        """Handle delete task button."""
        if self.current_task_id is not None:
            reply = QMessageBox.question(
                self, "确认删除", "确定要删除这个任务吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.task_manager.delete_task(self.current_task_id)
                self.current_task_id = None
                self.start_button.setEnabled(False)
                self.complete_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                self._load_tasks()
                self.task_changed.emit()

    def refresh(self):
        """Refresh the task list."""
        self._load_tasks()

    def get_current_task_id(self) -> int:
        """Get current selected task ID."""
        return self.current_task_id
