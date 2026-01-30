"""
Pomodoro timer widget module.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QComboBox, QProgressBar)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon

from core.pomodoro import PomodoroTimer, PomodoroState


class PomodoroWidget(QWidget):
    """Pomodoro timer widget."""

    # Signals
    pomodoro_completed = pyqtSignal(int)  # duration in seconds
    state_changed = pyqtSignal(PomodoroState)

    def __init__(self, db=None, parent=None):
        """
        Initialize pomodoro widget.

        Args:
            db: Database instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db
        self.current_task_id = None
        self._init_ui()
        self._init_timer()
        self._apply_styles()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("番茄时钟")
        title_label.setObjectName("timerLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Timer display
        self.timer_display = QLabel("25:00")
        self.timer_display.setObjectName("timerDisplay")
        self.timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timer_display)

        # Status label
        self.status_label = QLabel("准备开始")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)

        # Timer mode selector
        mode_layout = QHBoxLayout()
        mode_layout.addStretch()

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["工作", "短休息", "长休息"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)

        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.start_button = QPushButton("开始")
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(self._on_start_clicked)
        button_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("暂停")
        self.pause_button.setObjectName("pauseButton")
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)

        self.reset_button = QPushButton("重置")
        self.reset_button.setObjectName("resetButton")
        self.reset_button.clicked.connect(self._on_reset_clicked)
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)

        # Statistics
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)

        self.today_count_label = QLabel("今日: 0 个")
        stats_layout.addWidget(self.today_count_label)

        self.total_time_label = QLabel("累计: 0 分钟")
        stats_layout.addWidget(self.total_time_label)

        layout.addWidget(stats_frame)

        layout.addStretch()

    def _init_timer(self):
        """Initialize timer."""
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_timer_tick)

        self.pomodoro_timer = PomodoroTimer(
            on_tick=self._on_timer_tick_callback,
            on_state_change=self._on_state_change_callback
        )

        self._update_stats()

    def _apply_styles(self):
        """Apply styles to widget."""
        self.setFixedWidth(300)

    def _update_stats(self):
        """Update statistics display."""
        if self.db:
            stats = self.db.get_pomodoro_stats()
            self.today_count_label.setText(f"今日: {stats['today_count']} 个")
            total_minutes = stats['all_time_duration'] // 60
            self.total_time_label.setText(f"累计: {total_minutes} 分钟")

    def _on_mode_changed(self, index):
        """Handle mode change."""
        if self.pomodoro_timer.state == PomodoroState.IDLE:
            if index == 0:
                self.timer_display.setText("25:00")
            elif index == 1:
                self.timer_display.setText("05:00")
            else:
                self.timer_display.setText("15:00")

    def _on_start_clicked(self):
        """Handle start button click."""
        mode = self.mode_combo.currentIndex()
        if mode == 0:
            self.pomodoro_timer.start_work()
        elif mode == 1:
            self.pomodoro_timer.start_short_break()
        else:
            self.pomodoro_timer.start_long_break()

        self.timer.start()
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.mode_combo.setEnabled(False)

    def _on_pause_clicked(self):
        """Handle pause button click."""
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
        """Handle reset button click."""
        self.timer.stop()
        self.pomodoro_timer.reset()
        self.timer_display.setText("25:00")
        self.status_label.setText("准备开始")
        self.progress_bar.setValue(0)
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.pause_button.setText("暂停")
        self.mode_combo.setEnabled(True)

    def _on_timer_tick_callback(self, remaining: int):
        """Handle timer tick from pomodoro timer."""
        self.timer_display.setText(self.pomodoro_timer.format_time(remaining))

        # Update progress bar
        total = self.pomodoro_timer.get_duration()
        elapsed = self.pomodoro_timer.elapsed_seconds
        progress = int((elapsed / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress)

    def _on_state_change_callback(self, state: PomodoroState):
        """Handle state change from pomodoro timer."""
        self.status_label.setText(self._get_status_text())
        self.state_changed.emit(state)

    def _on_timer_tick(self):
        """Handle timer tick."""
        completed = self.pomodoro_timer.tick()
        if completed:
            self._on_pomodoro_completed()

    def _on_pomodoro_completed(self):
        """Handle pomodoro session completion."""
        self.timer.stop()

        duration = self.pomodoro_timer.get_actual_duration()
        start_time = self.pomodoro_timer.get_start_time()
        end_time = self.pomodoro_timer.get_end_time()

        # Save to database if it was a work session
        if self.pomodoro_timer.state == PomodoroState.WORKING and self.db:
            self.db.create_pomodoro(
                task_id=self.current_task_id,
                duration=duration,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat()
            )
            self._update_stats()

        self.pomodoro_completed.emit(duration)

        # Update UI
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.mode_combo.setEnabled(True)

        # Auto-switch mode suggestion
        if self.pomodoro_timer.state == PomodoroState.WORKING:
            self.status_label.setText("工作完成！开始休息吧")
            self.mode_combo.setCurrentIndex(1 if self.pomodoro_timer.work_sessions % 4 != 0 else 2)
        else:
            self.status_label.setText("休息完成！开始工作吧")
            self.mode_combo.setCurrentIndex(0)

    def _get_status_text(self) -> str:
        """Get status text based on current state."""
        state = self.pomodoro_timer.state
        if state == PomodoroState.WORKING:
            return "工作中"
        elif state == PomodoroState.SHORT_BREAK:
            return "短休息中"
        elif state == PomodoroState.LONG_BREAK:
            return "长休息中"
        elif state == PomodoroState.PAUSED:
            return "已暂停"
        else:
            return "准备开始"

    def set_task(self, task_id: int):
        """Set current task for pomodoro tracking."""
        self.current_task_id = task_id

    def reset(self):
        """Reset the timer."""
        self._on_reset_clicked()
