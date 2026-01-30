"""
Todo list widget module.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QLabel, QPushButton, QLineEdit,
                             QComboBox, QFrame, QTextEdit, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QBrush

from core.todo_manager import TaskManager, Task


class TodoWidget(QWidget):
    """Todo list widget."""

    # Signals
    task_selected = pyqtSignal(int)  # task_id
    task_changed = pyqtSignal()

    def __init__(self, db=None, parent=None):
        """
        Initialize todo widget.

        Args:
            db: Database instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db
        self.task_manager = TaskManager(db) if db else None
        self.current_task_id = None
        self._init_ui()
        self._load_tasks()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title_layout = QHBoxLayout()

        title_label = QLabel("待办事项")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Theme toggle
        self.theme_button = QPushButton("深色")
        self.theme_button.setFixedWidth(60)
        self.theme_button.clicked.connect(self._on_theme_toggle)
        title_layout.addWidget(self.theme_button)

        layout.addLayout(title_layout)

        # Filter and search
        filter_layout = QHBoxLayout()

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部", "待办", "进行中", "已完成"])
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.filter_combo)

        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Task list
        self.task_list = QListWidget()
        self.task_list.setObjectName("taskList")
        self.task_list.itemClicked.connect(self._on_task_clicked)
        self.task_list.itemDoubleClicked.connect(self._on_task_double_clicked)
        layout.addWidget(self.task_list)

        # Add task section
        add_frame = QFrame()
        add_frame.setObjectName("addFrame")
        add_layout = QVBoxLayout(add_frame)
        add_layout.setSpacing(8)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("输入任务标题...")
        self.title_input.returnPressed.connect(self._on_add_task)
        add_layout.addWidget(self.title_input)

        # Priority and add button
        priority_layout = QHBoxLayout()

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["高优先级", "中优先级", "低优先级"])
        self.priority_combo.setCurrentIndex(1)
        priority_layout.addWidget(self.priority_combo)

        priority_layout.addStretch()

        self.add_button = QPushButton("添加任务")
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self._on_add_task)
        priority_layout.addWidget(self.add_button)

        add_layout.addLayout(priority_layout)
        layout.addWidget(add_frame)

        # Task actions
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        self.start_button = QPushButton("开始任务")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self._on_start_task)
        action_layout.addWidget(self.start_button)

        self.complete_button = QPushButton("完成")
        self.complete_button.setEnabled(False)
        self.complete_button.clicked.connect(self._on_complete_task)
        action_layout.addWidget(self.complete_button)

        self.delete_button = QPushButton("删除")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self._on_delete_task)
        action_layout.addWidget(self.delete_button)

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

        for task in tasks:
            self._add_task_item(task)

    def _add_task_item(self, task: Task):
        """Add a task to the list."""
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, task.id)

        # Create widget for item
        widget = self._create_task_widget(task)
        item.setSizeHint(widget.sizeHint())

        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, widget)

    def _create_task_widget(self, task: Task) -> QFrame:
        """Create a widget for displaying task."""
        frame = QFrame()
        frame.setObjectName("taskItem")

        layout = QVBoxLayout(frame)
        layout.setSpacing(4)

        # Title and priority
        title_layout = QHBoxLayout()

        title_label = QLabel(task.title)
        title_label.setWordWrap(True)
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        priority_label = QLabel(f"[{task.priority_label}]")
        priority_label.setObjectName(f"priority{task.priority}")
        title_layout.addWidget(priority_label)

        layout.addLayout(title_layout)

        # Status
        status_label = QLabel(task.status_label)
        status_label.setObjectName(f"status{task.status}")
        status_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(status_label)

        return frame

    def _on_filter_changed(self):
        """Handle filter change."""
        self._load_tasks()

    def _on_task_clicked(self, item):
        """Handle task click."""
        task_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_task_id = task_id
        self.task_selected.emit(task_id)

        # Update button states
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
            self._edit_task(task)

    def _edit_task(self, task: Task):
        """Edit a task."""
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

        priority = self.priority_combo.currentIndex() + 1  # 1, 2, or 3

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

    def _on_theme_toggle(self):
        """Toggle theme."""
        self.theme_button.setText("浅色" if self.theme_button.text() == "深色" else "深色")
        # Emit signal to parent for theme change
        from PyQt6.QtCore import QEvent
        self.window().toggle_theme()

    def refresh(self):
        """Refresh the task list."""
        self._load_tasks()

    def get_current_task_id(self) -> int:
        """Get current selected task ID."""
        return self.current_task_id
