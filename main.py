#!/usr/bin/env python3
"""
Main entry point for Pomodoro Todo application.
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QMessageBox

from ui.main_window import MainWindow
from core.updater import Updater
from ui.update_dialog import UpdateDialog


def main():
    """Application entry point."""
    # Enable high DPI scaling BEFORE creating QApplication
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set application metadata
    app.setApplicationName("番茄时钟 + TodoList")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PomodoroTodo")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Load saved theme preference
    from core.database import Database
    db = Database()
    is_dark = db.get_setting("dark_theme", "0") == "1"
    if is_dark:
        window.is_dark_theme = True
        window._apply_theme()

    # Schedule update check after window loads
    def _check_update_on_startup():
        """启动时检查更新"""
        try:
            updater = Updater()
            is_new, latest_version = updater.check_update()
            if is_new:
                info = updater.get_version_info()
                # 延迟显示更新对话框，让主窗口先显示
                dialog = UpdateDialog(
                    updater.current_version,
                    latest_version,
                    info.get('body', ''),
                    window
                )
                dialog.exec()
        except Exception:
            pass  # 更新检查失败不影响正常使用

    QTimer.singleShot(2000, _check_update_on_startup)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
