"""
Fresh Pomodoro widget - Clean and modern design.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QSpinBox, QGridLayout,
                             QSpacerItem, QSizePolicy)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt

from core.pomodoro import PomodoroTimer, PomodoroState


class DurationSelector(QWidget):
    """Duration selector with clean layout."""

    duration_changed = pyqtSignal()

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self._init_ui()
        self._load_config()

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.work_spin.setEnabled(enabled)
        self.short_spin.setEnabled(enabled)
        self.long_spin.setEnabled(enabled)

    def _init_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 2, 0, 2)

        # Work row
        layout.addWidget(QLabel("工作"), 0, 0, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 120)
        self.work_spin.setValue(25)
        self.work_spin.setFixedWidth(45)
        self.work_spin.valueChanged.connect(self._on_duration_changed)
        layout.addWidget(self.work_spin, 0, 1, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(QLabel("分钟"), 0, 2, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Short break row
        layout.addWidget(QLabel("短休"), 1, 0, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.short_spin = QSpinBox()
        self.short_spin.setRange(1, 60)
        self.short_spin.setValue(5)
        self.short_spin.setFixedWidth(45)
        self.short_spin.valueChanged.connect(self._on_duration_changed)
        layout.addWidget(self.short_spin, 1, 1, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(QLabel("分钟"), 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Long break row
        layout.addWidget(QLabel("长休"), 2, 0, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.long_spin = QSpinBox()
        self.long_spin.setRange(1, 120)
        self.long_spin.setValue(15)
        self.long_spin.setFixedWidth(45)
        self.long_spin.valueChanged.connect(self._on_duration_changed)
        layout.addWidget(self.long_spin, 2, 1, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(QLabel("分钟"), 2, 2, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Reset button
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setFixedSize(36, 20)
        self.reset_btn.clicked.connect(self._reset_config)
        layout.addWidget(self.reset_btn, 3, 2, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 0)

    def _on_duration_changed(self):
        self._save_config()
        self.duration_changed.emit()

    def _load_config(self):
        if self.db:
            self.work_spin.setValue(int(self.db.get_setting("work_duration", "25")))
            self.short_spin.setValue(int(self.db.get_setting("short_break_duration", "5")))
            self.long_spin.setValue(int(self.db.get_setting("long_break_duration", "15")))

    def _save_config(self):
        if self.db:
            self.db.set_setting("work_duration", str(self.work_spin.value()))
            self.db.set_setting("short_break_duration", str(self.short_spin.value()))
            self.db.set_setting("long_break_duration", str(self.long_spin.value()))

    def _reset_config(self):
        self.work_spin.setValue(25)
        self.short_spin.setValue(5)
        self.long_spin.setValue(15)

    def get_work_duration(self):
        return self.work_spin.value()

    def get_short_break_duration(self):
        return self.short_spin.value()

    def get_long_break_duration(self):
        return self.long_spin.value()


class PomodoroWidget(QWidget):
    pomodoro_completed = pyqtSignal(int)
    state_changed = pyqtSignal(PomodoroState)

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_task_id = None
        self._init_ui()
        self._init_timer()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        card = QFrame()
        card.setObjectName("timerCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(10, 10, 10, 10)

        # Timer display
        self.timer_display = QLabel("25:00")
        self.timer_display.setObjectName("timerDisplay")
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.timer_display)

        # Status
        self.status_label = QLabel("准备开始")
        self.status_label.setObjectName("timerStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.status_label)

        # Mode buttons
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(6)

        self.work_btn = QPushButton("工作 25分钟")
        self.work_btn.setCheckable(True)
        self.work_btn.setChecked(True)
        self.work_btn.setObjectName("workButton")
        self.work_btn.setFixedSize(78, 26)
        self.work_btn.clicked.connect(lambda: self._on_mode_selected(0))
        mode_layout.addWidget(self.work_btn)

        self.short_break_btn = QPushButton("短休 5分钟")
        self.short_break_btn.setCheckable(True)
        self.short_break_btn.setObjectName("shortBreakButton")
        self.short_break_btn.setFixedSize(78, 26)
        self.short_break_btn.clicked.connect(lambda: self._on_mode_selected(1))
        mode_layout.addWidget(self.short_break_btn)

        self.long_break_btn = QPushButton("长休 15分钟")
        self.long_break_btn.setCheckable(True)
        self.long_break_btn.setObjectName("longBreakButton")
        self.long_break_btn.setFixedSize(78, 26)
        self.long_break_btn.clicked.connect(lambda: self._on_mode_selected(2))
        mode_layout.addWidget(self.long_break_btn)

        card_layout.addLayout(mode_layout)

        # Duration selector
        self.duration_selector = DurationSelector(self.db)
        self.duration_selector.duration_changed.connect(self._on_duration_changed)
        card_layout.addWidget(self.duration_selector)

        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.start_button = QPushButton("开始")
        self.start_button.setObjectName("startButton")
        self.start_button.setProperty("class", "primary")
        self.start_button.setFixedSize(48, 26)
        self.start_button.clicked.connect(self._on_start_clicked)
        btn_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("暂停")
        self.pause_button.setObjectName("pauseButton")
        self.pause_button.setFixedSize(48, 26)
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.pause_button.setEnabled(False)
        btn_layout.addWidget(self.pause_button)

        self.reset_button = QPushButton("重置")
        self.reset_button.setObjectName("resetButton")
        self.reset_button.setFixedSize(48, 26)
        self.reset_button.clicked.connect(self._on_reset_clicked)
        btn_layout.addWidget(self.reset_button)

        card_layout.addLayout(btn_layout)

        # Stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        self.today_count_label = QLabel("0")
        self.today_count_label.setProperty("class", "stats-num")
        stats_layout.addWidget(self.today_count_label)

        today_label = QLabel("今日")
        today_label.setProperty("class", "stats-label")
        stats_layout.addWidget(today_label)

        stats_layout.addSpacing(8)

        self.total_time_label = QLabel("0分钟")
        self.total_time_label.setProperty("class", "stats-num")
        stats_layout.addWidget(self.total_time_label)

        total_label = QLabel("累计")
        total_label.setProperty("class", "stats-label")
        stats_layout.addWidget(total_label)

        stats_layout.addStretch()
        card_layout.addLayout(stats_layout)

        layout.addWidget(card)

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
        work = self.duration_selector.get_work_duration()
        short = self.duration_selector.get_short_break_duration()
        long = self.duration_selector.get_long_break_duration()

        self.work_btn.setText(f"工作 {work}分钟")
        self.short_break_btn.setText(f"短休 {short}分钟")
        self.long_break_btn.setText(f"长休 {long}分钟")

        if self.pomodoro_timer.state == PomodoroState.IDLE:
            if self.work_btn.isChecked():
                self.timer_display.setText(f"{work:02d}:00")
            elif self.short_break_btn.isChecked():
                self.timer_display.setText(f"{short:02d}:00")
            else:
                self.timer_display.setText(f"{long:02d}:00")

    def _on_duration_changed(self):
        self._update_button_styles()

    def _on_mode_selected(self, mode):
        if self.pomodoro_timer.state == PomodoroState.IDLE:
            self.work_btn.setChecked(mode == 0)
            self.short_break_btn.setChecked(mode == 1)
            self.long_break_btn.setChecked(mode == 2)
            self._update_button_styles()

    def _on_start_clicked(self):
        if self.work_btn.isChecked():
            d = self.duration_selector.get_work_duration() * 60
            self.pomodoro_timer.WORK_DURATION = d
            self.pomodoro_timer.start_work()
        elif self.short_break_btn.isChecked():
            d = self.duration_selector.get_short_break_duration() * 60
            self.pomodoro_timer.SHORT_BREAK_DURATION = d
            self.pomodoro_timer.start_short_break()
        else:
            d = self.duration_selector.get_long_break_duration() * 60
            self.pomodoro_timer.LONG_BREAK_DURATION = d
            self.pomodoro_timer.start_long_break()

        self.timer.start()
        self.start_button.setEnabled(False)
        self.start_button.setText("运行中")
        self.pause_button.setEnabled(True)
        self.duration_selector.setEnabled(False)

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
        self.start_button.setEnabled(True)
        self.start_button.setText("开始")
        self.pause_button.setEnabled(False)
        self.pause_button.setText("暂停")
        self.duration_selector.setEnabled(True)

    def _on_timer_tick_callback(self, remaining):
        self.timer_display.setText(self.pomodoro_timer.format_time(remaining))

    def _on_state_change_callback(self, state):
        self.status_label.setText(self._get_status_text())
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

        self.start_button.setEnabled(True)
        self.start_button.setText("开始")
        self.pause_button.setEnabled(False)
        self.duration_selector.setEnabled(True)

        if self.pomodoro_timer.state == PomodoroState.WORKING:
            self.status_label.setText("工作完成！开始休息吧")
            self.short_break_btn.setChecked(True)
            short = self.duration_selector.get_short_break_duration()
            self.timer_display.setText(f"{short:02d}:00")
        else:
            self.status_label.setText("休息完成！开始工作吧")
            self.work_btn.setChecked(True)
            work = self.duration_selector.get_work_duration()
            self.timer_display.setText(f"{work:02d}:00")

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
            self.today_count_label.setText(str(stats['today_count']))
            m = stats['all_time_duration'] // 60
            h = m // 60
            mins = m % 60
            if h > 0:
                self.total_time_label.setText(f"{h}h{mins}m")
            else:
                self.total_time_label.setText(f"{mins}分钟")

    def set_task(self, task_id):
        self.current_task_id = task_id
