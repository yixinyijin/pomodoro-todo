"""
Fresh and clean design - Blue purple theme with medium weight fonts.
"""

# 蓝紫色主题
LIGHT_THEME = {
    "primary": "#7C4DFF",         # 主色 - 明亮蓝紫
    "primary_hover": "#651FFF",   # 主色悬停
    "primary_light": "#E8EAF6",   # 浅色背景
    "secondary": "#00BCD4",       # 辅助色 - 青色
    "background": "#FAFBFC",      # 页面背景
    "surface": "#FFFFFF",         # 卡片背景
    "border": "#E8E8E8",          # 边框色
    "text_primary": "#212121",    # 主文字
    "text_secondary": "#757575",  # 次要文字
    "divider": "#F0F0F0",         # 分割线
}

DARK_THEME = {
    "primary": "#B388FF",         # 主色 - 亮紫
    "primary_hover": "#D1C4E9",   # 主色悬停
    "primary_light": "#311B92",   # 浅色背景
    "secondary": "#18FFFF",       # 辅助色
    "background": "#121212",      # 页面背景
    "surface": "#1E1E1E",         # 卡片背景
    "border": "#333333",          # 边框色
    "text_primary": "#FFFFFF",    # 主文字
    "text_secondary": "#9E9E9E",  # 次要文字
    "divider": "#2C2C2C",         # 分割线
}


def get_stylesheet(theme: dict = None) -> str:
    if theme is None:
        theme = LIGHT_THEME

    return f"""
    /* 基础设置 */
    * {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 13px;
        font-weight: 400;
    }}

    /* 主窗口和部件 */
    QMainWindow, QWidget {{
        background-color: {theme['background']};
        color: {theme['text_primary']};
    }}

    /* 卡片样式 */
    #timerCard, #taskCard {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 10px;
    }}

    /* 标题 */
    #sectionTitle {{
        font-size: 15px;
        font-weight: 600;
        color: {theme['text_primary']};
    }}

    #timerLabel {{
        font-size: 14px;
        font-weight: 600;
        color: {theme['primary']};
    }}

    /* 按钮基础样式 */
    QPushButton {{
        background-color: {theme['surface']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 5px 10px;
        min-height: 20px;
    }}

    QPushButton:hover {{
        background-color: {theme['divider']};
        border-color: {theme['primary']};
        background-color: {theme['primary_light']};
    }}

    QPushButton:disabled {{
        opacity: 0.5;
        background-color: {theme['divider']};
    }}

    /* 主按钮 */
    QPushButton.primary {{
        background-color: {theme['primary']};
        color: white;
        border: none;
    }}

    QPushButton.primary:hover {{
        background-color: {theme['primary_hover']};
    }}

    /* 成功按钮 */
    QPushButton.success {{
        background-color: {theme['secondary']};
        color: white;
        border: none;
    }}

    /* 模式切换按钮 */
    #workButton, #shortBreakButton, #longBreakButton {{
        background-color: {theme['surface']};
        color: {theme['text_primary']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 5px 8px;
        font-size: 12px;
    }}

    #workButton:checked, #shortBreakButton:checked, #longBreakButton:checked {{
        background-color: {theme['primary']};
        color: white;
        border-color: {theme['primary']};
    }}

    QPushButton.primary:checked {{
        background-color: {theme['primary_hover']};
    }}

    /* 时间显示 */
    #timerDisplay {{
        font-size: 32px;
        font-weight: 500;
        color: {theme['primary']};
        background-color: transparent;
        border: none;
        letter-spacing: 1px;
    }}

    /* 状态文字 */
    #timerStatus {{
        font-size: 12px;
        color: {theme['text_secondary']};
    }}

    /* 任务列表 */
    QListWidget {{
        background-color: transparent;
        border: none;
        padding: 0px;
    }}

    QListWidget::item {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 6px;
        margin-bottom: 4px;
    }}

    QListWidget::item:hover:!selected {{
        border: 1px solid {theme['primary']};
        background-color: {theme['primary_light']};
    }}

    QListWidget::item:selected {{
        background-color: {theme['primary']};
        color: white;
        border-color: {theme['primary']};
        border-radius: 4px;
    }}

    /* 任务标题 */
    #taskTitle {{
        font-size: 13px;
        font-weight: 500;
    }}

    /* 输入框 */
    QLineEdit {{
        background-color: {theme['background']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 6px 10px;
    }}

    QLineEdit:focus {{
        border-color: {theme['primary']};
        outline: none;
    }}

    /* 下拉框 */
    QComboBox {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 5px 10px;
        font-size: 12px;
    }}

    /* 优先级标签 */
    .priority-high {{
        color: #E53935;
        font-size: 11px;
        font-weight: 500;
    }}

    .priority-medium {{
        color: #FB8C00;
        font-size: 11px;
        font-weight: 500;
    }}

    .priority-low {{
        color: {theme['secondary']};
        font-size: 11px;
        font-weight: 500;
    }}

    /* 状态徽章 */
    .status-badge {{
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 10px;
    }}

    .status-pending {{
        color: {theme['text_secondary']};
        background-color: {theme['divider']};
    }}

    .status-progress {{
        color: {theme['primary']};
    }}

    .status-completed {{
        color: {theme['secondary']};
        background-color: {theme['secondary']}25;
    }}

    /* 统计数据 */
    .stats-num {{
        font-size: 18px;
        font-weight: 500;
        color: {theme['primary']};
    }}

    .stats-label {{
        font-size: 11px;
        color: {theme['text_secondary']};
    }}

    /* 时间选择标签 */
    #durationLabel {{
        font-size: 12px;
        color: {theme['text_secondary']};
    }}

    /* 滚动条 */
    QScrollBar:vertical {{
        background-color: transparent;
        width: 6px;
        border-radius: 3px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {theme['border']};
        border-radius: 3px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {theme['primary']};
    }}

    /* 菜单栏 */
    QMenuBar {{
        background-color: {theme['surface']};
        border-bottom: 1px solid {theme['border']};
        padding: 4px 8px;
    }}

    QMenu {{
        background-color: {theme['surface']};
        border: 1px solid {theme['border']};
        border-radius: 4px;
        padding: 0px;
    }}

    QMenu::item {{
        padding: 6px 12px;
        border-radius: 4px;
    }}

    QMenu::item:selected {{
        color: {theme['primary']};
    }}

    /* 状态栏 */
    QStatusBar {{
        background-color: {theme['surface']};
        border-top: 1px solid {theme['border']};
    }}
    """
