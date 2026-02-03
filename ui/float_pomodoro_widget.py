"""
Floating Pomodoro widget - Independent window design.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QGraphicsDropShadowEffect,
                             QSizePolicy, QSpinBox, QInputDialog)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt, QPoint, QEvent
from PyQt6.QtGui import QColor, QCursor

from core.pomodoro import PomodoroTimer, PomodoroState


class FloatPomodoroWidget(QDialog):
    """Floating Pomodoro timer dialog - independent window."""

    pomodoro_completed = pyqtSignal(int)
    state_changed = pyqtSignal(PomodoroState)

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_task_id = None
        # Load duration settings from database
        self._work_duration = int(db.get_setting("work_duration", "25")) if db else 25
        self._short_break = int(db.get_setting("short_break_duration", "5")) if db else 5
        self._long_break = int(db.get_setting("long_break_duration", "15")) if db else 15

        self.setWindowTitle("番茄时钟")
        self.setFixedSize(300, 320)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                          Qt.WindowType.WindowStaysOnTopHint |
                          Qt.WindowType.Dialog)
        self._init_ui()
        self._init_timer()
        self._setup_shadow()

    def _setup_shadow(self):
        """Add drop shadow for modern look."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.card_frame.setGraphicsEffect(shadow)

    def _init_ui(self):
        # Main layout with header for buttons
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Top bar with window buttons
        top_bar = QFrame()
        top_bar.setFixedHeight(32)
        top_bar.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(6, 0, 6, 0)
        top_bar_layout.setSpacing(4)

        # Left: Title with icon
        title_label = QLabel("番茄时钟")
        title_label.setStyleSheet("font-size: 11px; font-weight: 500;")
        top_bar_layout.addWidget(title_label)

        # Spacer for dragging
        top_bar_layout.addStretch()

        # Right: Window buttons with icons
        btn_style = """
            QPushButton {
                font-size: 11px;
                text-align: center;
                border: 1px solid #DDD;
                border-radius: 3px;
                min-width: 28px;
                padding: 2px 6px;
            }
            QPushButton:hover {
                border-color: #7C4DFF;
                background-color: #F5F0FF;
            }
        """

        # Pin button - different styles for pinned/unpinned state
        self.pin_style_unchecked = """
            QPushButton {
                font-size: 11px;
                text-align: center;
                border: 1px solid #DDD;
                border-radius: 3px;
                min-width: 28px;
                padding: 2px 6px;
                color: #666;
            }
            QPushButton:hover {
                border-color: #7C4DFF;
                background-color: #F5F0FF;
            }
        """
        self.pin_style_checked = """
            QPushButton {
                font-size: 11px;
                text-align: center;
                border: 1px solid #7C4DFF;
                border-radius: 3px;
                min-width: 28px;
                padding: 2px 6px;
                background-color: #7C4DFF;
                color: white;
            }
            QPushButton:hover {
                border-color: #651FFF;
                background-color: #651FFF;
            }
        """

        self.pin_btn = QPushButton("T")
        self.pin_btn.setFixedSize(32, 24)
        self.pin_btn.setCheckable(True)
        self.pin_btn.setChecked(True)
        self.pin_btn.setToolTip("取消置顶")
        self.pin_btn.setStyleSheet(self.pin_style_checked)
        self.pin_btn.clicked.connect(self._on_toggle_pin)
        top_bar_layout.addWidget(self.pin_btn)

        self.minimize_btn = QPushButton("_")
        self.minimize_btn.setFixedSize(32, 24)
        self.minimize_btn.setToolTip("最小化")
        self.minimize_btn.setStyleSheet(btn_style)
        self.minimize_btn.clicked.connect(self.hide)
        top_bar_layout.addWidget(self.minimize_btn)

        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(32, 24)
        self.close_btn.setToolTip("关闭")
        self.close_btn.setStyleSheet(btn_style)
        self.close_btn.clicked.connect(self.hide)
        top_bar_layout.addWidget(self.close_btn)

        main_layout.addWidget(top_bar)

        # Enable drag on top bar
        top_bar.mousePressEvent = self._mouse_press_event
        top_bar.mouseMoveEvent = self._mouse_move_event
        top_bar.mouseReleaseEvent = self._mouse_release_event
        title_label.mousePressEvent = self._mouse_press_event
        title_label.mouseMoveEvent = self._mouse_move_event
        title_label.mouseReleaseEvent = self._mouse_release_event
        self._dragging = False
        self._drag_position = QPoint()

        # Card container with shadow
        self.card_frame = QFrame()
        self.card_frame.setObjectName("timerCard")
        self.card_frame.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.card_frame.installEventFilter(self)
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setSpacing(4)
        card_layout.setContentsMargins(8, 8, 8, 8)

        # Timer display (scroll to edit)
        self.timer_display = QLabel("25:00")
        self.timer_display.setObjectName("timerDisplay")
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_display.setStyleSheet("font-size: 28px; font-weight: 500;")
        self.timer_display.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.timer_display.setToolTip("滚动滚轮修改时长")
        self.timer_display.mouseDoubleClickEvent = self._on_timer_double_click
        card_layout.addWidget(self.timer_display)

        # Status
        self.status_label = QLabel("准备开始")
        self.status_label.setObjectName("timerStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #666;")
        card_layout.addWidget(self.status_label)

        # Mode buttons
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(4)

        self.work_btn = QPushButton("工作")
        self.work_btn.setCheckable(True)
        self.work_btn.setChecked(True)
        self.work_btn.setObjectName("workButton")
        self.work_btn.setProperty("class", "primary")
        self.work_btn.setFixedSize(48, 24)
        self.work_btn.clicked.connect(lambda: self._on_mode_selected(0))
        mode_layout.addWidget(self.work_btn)

        self.short_break_btn = QPushButton("短休")
        self.short_break_btn.setCheckable(True)
        self.short_break_btn.setObjectName("shortBreakButton")
        self.short_break_btn.setProperty("class", "primary")
        self.short_break_btn.setFixedSize(48, 24)
        self.short_break_btn.clicked.connect(lambda: self._on_mode_selected(1))
        mode_layout.addWidget(self.short_break_btn)

        self.long_break_btn = QPushButton("长休")
        self.long_break_btn.setCheckable(True)
        self.long_break_btn.setObjectName("longBreakButton")
        self.long_break_btn.setProperty("class", "primary")
        self.long_break_btn.setFixedSize(48, 24)
        self.long_break_btn.clicked.connect(lambda: self._on_mode_selected(2))
        mode_layout.addWidget(self.long_break_btn)

        card_layout.addLayout(mode_layout)

        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        self.start_button = QPushButton("开始")
        self.start_button.setObjectName("startButton")
        self.start_button.setProperty("class", "primary")
        self.start_button.setFixedSize(48, 24)
        self.start_button.clicked.connect(self._on_start_clicked)
        btn_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("暂停")
        self.pause_button.setObjectName("pauseButton")
        self.pause_button.setFixedSize(48, 24)
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.pause_button.setEnabled(False)
        btn_layout.addWidget(self.pause_button)

        self.reset_button = QPushButton("重置")
        self.reset_button.setObjectName("resetButton")
        self.reset_button.setFixedSize(48, 24)
        self.reset_button.clicked.connect(self._on_reset_clicked)
        btn_layout.addWidget(self.reset_button)

        card_layout.addLayout(btn_layout)

        # Stats row - centered with different colors
        self.stats_label = QLabel("<span style='color: #888;'>今日</span> <span style='color: #7C4DFF; font-weight: 600;'>0</span>")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.setStyleSheet("font-size: 22px; font-weight: 500;")
        card_layout.addWidget(self.stats_label)

        main_layout.addWidget(self.card_frame)

    def _mouse_press_event(self, event):
        """Start dragging."""
        self._dragging = True
        self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        event.accept()

    def _mouse_move_event(self, event):
        """Drag the window."""
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def _mouse_release_event(self, event):
        """Stop dragging."""
        self._dragging = False
        event.accept()

    def _init_timer(self):
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_timer_tick)

        self.pomodoro_timer = PomodoroTimer(
            on_tick=self._on_timer_tick_callback,
            on_state_change=self._on_state_change_callback
        )

        self._update_stats()
        self._update_button_styles()

    def _update_button_styles(self):
        if self.pomodoro_timer.state == PomodoroState.IDLE:
            if self.work_btn.isChecked():
                self.timer_display.setText(f"{self._work_duration:02d}:00")
            elif self.short_break_btn.isChecked():
                self.timer_display.setText(f"{self._short_break:02d}:00")
            else:
                self.timer_display.setText(f"{self._long_break:02d}:00")

    def _on_mode_selected(self, mode):
        if self.pomodoro_timer.state == PomodoroState.IDLE:
            self.work_btn.setChecked(mode == 0)
            self.short_break_btn.setChecked(mode == 1)
            self.long_break_btn.setChecked(mode == 2)
            self._update_button_styles()

    def _on_start_clicked(self):
        work = self._work_duration
        short = self._short_break
        long = self._long_break

        if self.work_btn.isChecked():
            d = work * 60
            self.pomodoro_timer.WORK_DURATION = d
            self.pomodoro_timer.start_work()
        elif self.short_break_btn.isChecked():
            d = short * 60
            self.pomodoro_timer.SHORT_BREAK_DURATION = d
            self.pomodoro_timer.start_short_break()
        else:
            d = long * 60
            self.pomodoro_timer.LONG_BREAK_DURATION = d
            self.pomodoro_timer.start_long_break()

        self.timer.start()
        self._update_control_buttons()

    def _on_pause_clicked(self):
        if self.pomodoro_timer.state == PomodoroState.PAUSED:
            self.pomodoro_timer.resume()
            self.timer.start()
            self.pause_button.setText("暂停")
            self.status_label.setText(self._get_status_text())
        else:
            self.pomodoro_timer.pause()
            self.timer.stop()
            self.pause_button.setText("继续")
            self.status_label.setText("已暂停")

    def _on_reset_clicked(self):
        self.timer.stop()
        self.pomodoro_timer.reset()
        self._update_button_styles()
        self.status_label.setText("准备开始")
        self._update_control_buttons()

    def _update_control_buttons(self):
        """根据计时器状态更新控制按钮"""
        state = self.pomodoro_timer.state

        # 模式按钮：运行中禁用，暂停时也禁用
        is_working = state in (PomodoroState.WORKING, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK)
        is_paused = state == PomodoroState.PAUSED
        is_idle = state == PomodoroState.IDLE

        self.work_btn.setEnabled(is_idle)
        self.short_break_btn.setEnabled(is_idle)
        self.long_break_btn.setEnabled(is_idle)

        # 开始/暂停/重置按钮
        self.start_button.setEnabled(is_idle or is_paused)
        self.start_button.setText("开始" if is_idle else "运行")
        self.pause_button.setEnabled(is_working or is_paused)
        self.pause_button.setText("暂停" if is_working else "继续")

    def _on_toggle_pin(self, checked):
        """Toggle always on top."""
        # Check if flag is already in correct state to avoid unnecessary recreation
        has_flag = self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
        if checked == has_flag:
            return

        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            self.pin_btn.setToolTip("取消置顶")
            self.pin_btn.setStyleSheet(self.pin_style_checked)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            self.pin_btn.setToolTip("置顶")
            self.pin_btn.setStyleSheet(self.pin_style_unchecked)
        self.show()

    def eventFilter(self, obj, event):
        """Filter events for wheel handling."""
        if obj == self.card_frame and event.type() == QEvent.Type.Wheel:
            self._on_card_wheel(event)
            return True
        return super().eventFilter(obj, event)

    def _on_timer_double_click(self, event):
        """Show hint that wheel can be used."""
        pass

    def _on_card_wheel(self, event):
        """Adjust timer duration with mouse wheel."""
        if self.pomodoro_timer.state != PomodoroState.IDLE:
            return

        delta = event.angleDelta().y()
        if delta == 0:
            return

        # Determine current mode
        if self.work_btn.isChecked():
            setting_key = "work_duration"
            self._work_duration = max(1, min(120, self._work_duration + (1 if delta > 0 else -1)))
            minutes = self._work_duration
        elif self.short_break_btn.isChecked():
            setting_key = "short_break_duration"
            self._short_break = max(1, min(60, self._short_break + (1 if delta > 0 else -1)))
            minutes = self._short_break
        else:
            setting_key = "long_break_duration"
            self._long_break = max(1, min(120, self._long_break + (1 if delta > 0 else -1)))
            minutes = self._long_break

        # Save to database
        if self.db:
            self.db.set_setting(setting_key, str(minutes))

        # Update display
        self.timer_display.setText(f"{minutes:02d}:00")

    def _on_timer_tick_callback(self, remaining):
        self.timer_display.setText(self.pomodoro_timer.format_time(remaining))

    def _on_state_change_callback(self, state):
        self.status_label.setText(self._get_status_text())
        self._update_control_buttons()
        self.state_changed.emit(state)

    def _on_timer_tick(self):
        completed = self.pomodoro_timer.tick()
        if completed:
            self._on_pomodoro_completed()

    def _on_pomodoro_completed(self):
        self.timer.stop()

        duration = self.pomodoro_timer.get_actual_duration()
        start = self.pomodoro_timer.get_start_time()
        end = self.pomodoro_timer.get_end_time()

        if (self.pomodoro_timer.state == PomodoroState.WORKING and self.db
                and self.current_task_id is not None):
            self.db.create_pomodoro(
                task_id=self.current_task_id,
                duration=duration,
                start_time=start.isoformat(),
                end_time=end.isoformat()
            )
            self._update_stats()

        self.pomodoro_completed.emit(duration)

        if self.pomodoro_timer.state == PomodoroState.WORKING:
            self.status_label.setText("工作完成！开始休息吧")
            self.short_break_btn.setChecked(True)
            self.work_btn.setChecked(False)
            self.long_break_btn.setChecked(False)
            short = self._short_break
            self.timer_display.setText(f"{short:02d}:00")
        else:
            self.status_label.setText("休息完成！开始工作吧")
            self.work_btn.setChecked(True)
            self.short_break_btn.setChecked(False)
            self.long_break_btn.setChecked(False)
            work = self._work_duration
            self.timer_display.setText(f"{work:02d}:00")

        # 同步更新所有按钮状态
        self._update_control_buttons()

    def _get_status_text(self):
        state = self.pomodoro_timer.state
        if state == PomodoroState.WORKING:
            return "专注于当前任务"
        elif state == PomodoroState.SHORT_BREAK:
            return "短暂休息中..."
        elif state == PomodoroState.LONG_BREAK:
            return "长时间休息中..."
        elif state == PomodoroState.PAUSED:
            return "计时已暂停"
        return "准备开始"

    def _update_stats(self):
        if self.db:
            stats = self.db.get_pomodoro_stats()
            self.stats_label.setText(f"今日 {stats['today_count']}")

    def set_task(self, task_id):
        self.current_task_id = task_id
