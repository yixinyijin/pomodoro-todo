"""
Modern main window with clean layout - TodoList focused with floating Pomodoro.
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QSplitter,
                             QMenu, QMessageBox, QLabel, QFrame, QToolBar,
                             QStatusBar)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QPixmap

from ui.todo_widget import TodoWidget
from ui.styles import get_stylesheet, LIGHT_THEME, DARK_THEME
from ui.float_pomodoro_widget import FloatPomodoroWidget
from core.database import Database


class MainWindow(QMainWindow):
    """Modern main application window - TodoList with floating Pomodoro."""

    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.db = Database()
        self.is_dark_theme = False
        self._float_pomodoro = None
        self._init_ui()
        self._apply_theme()

    def _init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("待办事项 + 番茄时钟")
        self.setMinimumSize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout - full screen for todo
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Todo widget (full width now)
        self.todo_widget = TodoWidget(self.db)
        self.todo_widget.task_changed.connect(self._on_task_changed)
        main_layout.addWidget(self.todo_widget)

        # Menu bar
        self._create_menu_bar()

        # Tool bar
        self._create_toolbar()

        # Status bar
        self.statusBar().showMessage("就绪")

    def _create_toolbar(self):
        """Create toolbar with quick actions."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setStyleSheet("QToolBar { spacing: 8px; padding: 4px; }")
        self.addToolBar(toolbar)

        # Toggle Pomodoro action
        self.toggle_pomo_action = QAction("番茄时钟", self)
        self.toggle_pomo_action.setCheckable(True)
        self.toggle_pomo_action.triggered.connect(self._toggle_pomodoro)
        toolbar.addAction(self.toggle_pomo_action)

        # Theme toggle action
        self.theme_action = QAction("深色模式", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(self.theme_action)

    def _create_menu_bar(self):
        """Create menu bar."""
        menu_bar = self.menuBar()

        # View menu
        view_menu = menu_bar.addMenu("视图")

        toggle_pomo_action = QAction("显示/隐藏番茄时钟", self)
        toggle_pomo_action.setShortcut("Ctrl+P")
        toggle_pomo_action.triggered.connect(self._toggle_pomodoro)
        view_menu.addAction(toggle_pomo_action)

        theme_action = QAction("切换主题", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)

        # Help menu
        help_menu = menu_bar.addMenu("帮助")

        check_update_action = QAction("检查更新", self)
        check_update_action.triggered.connect(self._on_check_update)
        help_menu.addAction(check_update_action)

        about_action = QAction("关于", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _toggle_pomodoro(self):
        """Toggle floating pomodoro window."""
        if self._float_pomodoro is None:
            self._float_pomodoro = FloatPomodoroWidget(self.db, self)
            self._float_pomodoro.pomodoro_completed.connect(self._on_pomodoro_completed)
            self._float_pomodoro.todo_widget = self.todo_widget  # Link for task selection

            # Position relative to main window
            geo = self.geometry()
            self._float_pomodoro.move(geo.right() - 290, geo.top() + 80)

            # Connect task selection
            self.todo_widget.task_selected.connect(self._float_pomodoro.set_task)

            self._float_pomodoro.show()
            self.toggle_pomo_action.setChecked(True)
        else:
            if self._float_pomodoro.isVisible():
                self._float_pomodoro.hide()
                self.toggle_pomo_action.setChecked(False)
            else:
                # Update position in case window moved
                geo = self.geometry()
                self._float_pomodoro.move(geo.right() - 290, geo.top() + 80)
                self._float_pomodoro.show()
                self.toggle_pomo_action.setChecked(True)

    def _apply_theme(self):
        """Apply current theme."""
        theme = DARK_THEME if self.is_dark_theme else LIGHT_THEME
        self.setStyleSheet(get_stylesheet(theme))

    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.is_dark_theme = not self.is_dark_theme
        self._apply_theme()

        # Update toolbar
        if self.is_dark_theme:
            self.theme_action.setText("浅色模式")
        else:
            self.theme_action.setText("深色模式")

        # Update floating pomodoro if exists
        if self._float_pomodoro:
            self._float_pomodoro.setStyleSheet(get_stylesheet(DARK_THEME if self.is_dark_theme else LIGHT_THEME))

        # Save preference
        self.db.set_setting("dark_theme", "1" if self.is_dark_theme else "0")

    def _on_pomodoro_completed(self, duration: int):
        """Handle pomodoro completion."""
        minutes = duration // 60
        self.statusBar().showMessage(f"番茄钟完成！专注了 {minutes} 分钟")

    def _on_task_changed(self):
        """Handle task change."""
        if self._float_pomodoro:
            self._float_pomodoro._update_stats()

    def _on_check_update(self):
        """检查更新"""
        from ui.update_dialog import UpdateCheckDialog
        dialog = UpdateCheckDialog(self)
        # 应用当前主题
        from ui.styles import get_stylesheet, LIGHT_THEME, DARK_THEME
        theme = DARK_THEME if self.is_dark_theme else LIGHT_THEME
        dialog.setStyleSheet(get_stylesheet(theme))
        dialog.exec()

    def _on_about(self):
        """Show about dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self, "关于",
            "<h2>待办事项 + 番茄时钟</h2>"
            "<p>一个结合番茄工作法和待办事项管理的桌面应用。</p>"
            "<hr>"
            "<p><b>快捷键:</b></p>"
            "<ul>"
            "<li>Ctrl+P - 显示/隐藏番茄时钟</li>"
            "<li>Ctrl+T - 切换主题</li>"
            "</ul>"
            "<p><small>Built with PyQt6</small></p>"
        )

    def closeEvent(self, event):
        """Handle close event."""
        # Close floating window too
        if self._float_pomodoro:
            self._float_pomodoro.close()
        event.accept()
