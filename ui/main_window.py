"""
Main window module.
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QSplitter,
                             QSystemTrayIcon, QMenu, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from ui.pomodoro_widget import PomodoroWidget
from ui.todo_widget import TodoWidget
from ui.styles import get_stylesheet, LIGHT_THEME, DARK_THEME
from core.database import Database
from core.pomodoro import PomodoroState


class MainWindow(QMainWindow):
    """Main application window."""

    # Signal for theme change
    theme_changed = pyqtSignal(bool)  # is_dark

    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.db = Database()
        self.is_dark_theme = False
        self._init_ui()
        self._init_tray_icon()
        self._apply_theme()
        self._setup_notifications()

    def _init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("番茄时钟 + TodoList")
        self.setMinimumSize(900, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Pomodoro widget
        self.pomodoro_widget = PomodoroWidget(self.db)
        self.pomodoro_widget.pomodoro_completed.connect(self._on_pomodoro_completed)
        splitter.addWidget(self.pomodoro_widget)

        # Todo widget
        self.todo_widget = TodoWidget(self.db)
        self.todo_widget.task_selected.connect(self._on_task_selected)
        self.todo_widget.task_changed.connect(self._on_task_changed)
        splitter.addWidget(self.todo_widget)

        # Set splitter sizes (40% / 60%)
        splitter.setSizes([360, 540])

        main_layout.addWidget(splitter)

        # Menu bar
        self._create_menu_bar()

        # Status bar
        self.statusBar().showMessage("就绪")

    def _create_menu_bar(self):
        """Create menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("文件")

        export_action = QAction("导出数据", self)
        export_action.triggered.connect(self._on_export_data)
        file_menu.addAction(export_action)

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menu_bar.addMenu("视图")

        theme_action = QAction("切换主题", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)

        # Help menu
        help_menu = menu_bar.addMenu("帮助")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _init_tray_icon(self):
        """Initialize system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("番茄时钟 + TodoList")

        # Create tray menu
        tray_menu = QMenu()
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def _setup_notifications(self):
        """Setup notification sound."""
        # Sound file path (will use system sound)
        self.notification_sound = None

    def _apply_theme(self):
        """Apply current theme."""
        theme = DARK_THEME if self.is_dark_theme else LIGHT_THEME
        self.setStyleSheet(get_stylesheet(theme))
        self.theme_changed.emit(self.is_dark_theme)

    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.is_dark_theme = not self.is_dark_theme
        self._apply_theme()

        # Save preference
        self.db.set_setting("dark_theme", "1" if self.is_dark_theme else "0")

    def _on_pomodoro_completed(self, duration: int):
        """Handle pomodoro completion."""
        minutes = duration // 60
        self.statusBar().showMessage(f"番茄钟完成！专注了 {minutes} 分钟")

        # Show notification
        self.tray_icon.showMessage(
            "番茄时钟",
            f"一个番茄钟已完成！ ({minutes} 分钟)",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def _on_task_selected(self, task_id: int):
        """Handle task selection."""
        self.pomodoro_widget.set_task(task_id)
        task = self.todo_widget.task_manager.get_task(task_id) if self.todo_widget.task_manager else None
        if task:
            self.statusBar().showMessage(f"已选择任务: {task.title}")

    def _on_task_changed(self):
        """Handle task change."""
        self.pomodoro_widget._update_stats()

    def _on_export_data(self):
        """Export data to file."""
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime
        import json

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出数据", f"pomodoro_export_{datetime.now().strftime('%Y%m%d')}.json",
            "JSON Files (*.json)"
        )

        if file_path:
            # Collect all data
            data = {
                "export_date": datetime.now().isoformat(),
                "tasks": self.db.get_all_tasks(),
                "pomodoros": self.db.get_all_pomodoros(),
                "stats": self.db.get_pomodoro_stats()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self, "导出成功", f"数据已导出到: {file_path}")

    def _on_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "关于",
            "番茄时钟 + TodoList\n\n"
            "一个结合番茄工作法和待办事项管理的桌面应用。\n\n"
            "快捷键:\n"
            "  Ctrl+T - 切换主题\n"
            "  Ctrl+Q - 退出"
        )

    def closeEvent(self, event):
        """Handle close event."""
        # Minimize to tray instead of closing
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()
