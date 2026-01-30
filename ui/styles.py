"""
Styles and themes for Pomodoro Todo application.
"""

# Light theme colors
LIGHT_THEME = {
    "primary": "#E74C3C",
    "primary_hover": "#C0392B",
    "secondary": "#3498DB",
    "secondary_hover": "#2980B9",
    "success": "#27AE60",
    "warning": "#F39C12",
    "background": "#FFFFFF",
    "surface": "#F8F9FA",
    "surface_hover": "#ECF0F1",
    "text_primary": "#2C3E50",
    "text_secondary": "#7F8C8D",
    "text_on_primary": "#FFFFFF",
    "border": "#BDC3C7",
    "shadow": "rgba(0, 0, 0, 0.1)",
    "priority_high": "#E74C3C",
    "priority_medium": "#F39C12",
    "priority_low": "#27AE60",
    "status_pending": "#95A5A6",
    "status_in_progress": "#3498DB",
    "status_completed": "#27AE60",
}

# Dark theme colors
DARK_THEME = {
    "primary": "#E74C3C",
    "primary_hover": "#C0392B",
    "secondary": "#3498DB",
    "secondary_hover": "#2980B9",
    "success": "#27AE60",
    "warning": "#F39C12",
    "background": "#1A1A2E",
    "surface": "#16213E",
    "surface_hover": "#0F3460",
    "text_primary": "#ECF0F1",
    "text_secondary": "#95A5A6",
    "text_on_primary": "#FFFFFF",
    "border": "#4A4A6A",
    "shadow": "rgba(0, 0, 0, 0.3)",
    "priority_high": "#E74C3C",
    "priority_medium": "#F39C12",
    "priority_low": "#27AE60",
    "status_pending": "#7F8C8D",
    "status_in_progress": "#3498DB",
    "status_completed": "#27AE60",
}


def get_stylesheet(theme: dict = None) -> str:
    """Get the application stylesheet."""
    if theme is None:
        theme = LIGHT_THEME

    return f"""
    * {{
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        font-size: 14px;
    }}

    QMainWindow {{
        background-color: {theme['background']};
    }}

    QWidget {{
        background-color: {theme['background']};
        color: {theme['text_primary']};
    }}

    /* Buttons */
    QPushButton {{
        background-color: {theme['surface']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 6px;
        padding: 8px 16px;
        min-width: 80px;
    }}

    QPushButton:hover {{
        background-color: {theme['surface_hover']};
    }}

    QPushButton:pressed {{
        background-color: {theme['border']};
    }}

    QPushButton.primary {{
        background-color: {theme['primary']};
        color: {theme['text_on_primary']};
        border: none;
    }}

    QPushButton.primary:hover {{
        background-color: {theme['primary_hover']};
    }}

    QPushButton.success {{
        background-color: {theme['success']};
        color: {theme['text_on_primary']};
        border: none;
    }}

    /* Timer Display */
    #timerDisplay {{
        font-size: 72px;
        font-weight: bold;
        color: {theme['primary']};
        background-color: transparent;
        border: none;
    }}

    #timerLabel {{
        font-size: 18px;
        color: {theme['text_secondary']};
    }}

    /* Task List */
    QListWidget {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
        padding: 4px;
    }}

    QListWidget::item {{
        background-color: {theme['surface']};
        border-radius: 6px;
        padding: 8px;
        margin-bottom: 4px;
    }}

    QListWidget::item:selected {{
        background-color: {theme['primary']};
        color: {theme['text_on_primary']};
    }}

    QListWidget::item:hover {{
        background-color: {theme['surface_hover']};
    }}

    /* Line Edit */
    QLineEdit {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 6px;
        padding: 8px 12px;
        selection-background-color: {theme['primary']};
        selection-color: {theme['text_on_primary']};
    }}

    QLineEdit:focus {{
        border-color: {theme['primary']};
    }}

    /* ComboBox */
    QComboBox {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 6px;
        padding: 6px 12px;
    }}

    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}

    QComboBox::down-arrow {{
        image: none;
        border: none;
    }}

    /* GroupBox */
    QGroupBox {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
        padding: 16px;
        margin-top: 8px;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 8px;
        padding: 0 4px;
        color: {theme['text_secondary']};
    }}

    /* Progress Bar */
    QProgressBar {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        text-align: center;
    }}

    QProgressBar::chunk {{
        background-color: {theme['primary']};
        border-radius: 4px;
    }}

    /* Status Label */
    #statusLabel {{
        font-size: 12px;
        color: {theme['text_secondary']};
    }}

    /* Priority Badge */
    .priority-high {{
        color: {theme['priority_high']};
        font-weight: bold;
    }}

    .priority-medium {{
        color: {theme['priority_medium']};
        font-weight: bold;
    }}

    .priority-low {{
        color: {theme['priority_low']};
        font-weight: bold;
    }}

    /* ScrollBar */
    QScrollBar:vertical {{
        background-color: {theme['surface']};
        width: 10px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {theme['border']};
        border-radius: 4px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {theme['text_secondary']};
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* Tooltip */
    QToolTip {{
        background-color: {theme['surface']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 4px;
    }}
    """
