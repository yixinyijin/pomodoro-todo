#!/usr/bin/env python3
"""
Main entry point for Pomodoro Todo application.
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set application metadata
    app.setApplicationName("番茄时钟 + TodoList")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PomodoroTodo")

    # Enable high DPI scaling
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

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

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
