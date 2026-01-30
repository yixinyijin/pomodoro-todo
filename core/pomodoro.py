"""
Pomodoro timer logic module.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Optional


class PomodoroState(Enum):
    """Pomodoro timer states."""
    IDLE = "idle"
    WORKING = "working"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    PAUSED = "paused"


class PomodoroTimer:
    """Pomodoro timer logic handler."""

    # Default durations in seconds
    WORK_DURATION = 25 * 60  # 25 minutes
    SHORT_BREAK_DURATION = 5 * 60  # 5 minutes
    LONG_BREAK_DURATION = 15 * 60  # 15 minutes

    def __init__(self, on_tick: Callable[[int], None], on_state_change: Callable[[PomodoroState], None]):
        """
        Initialize pomodoro timer.

        Args:
            on_tick: Callback for each timer tick (remaining seconds)
            on_state_change: Callback when state changes
        """
        self.on_tick = on_tick
        self.on_state_change = on_state_change

        self._state = PomodoroState.IDLE
        self._remaining_seconds = self.WORK_DURATION
        self._elapsed_seconds = 0
        self._start_time: Optional[datetime] = None
        self._work_sessions = 0

    @property
    def state(self) -> PomodoroState:
        """Get current state."""
        return self._state

    @property
    def remaining_seconds(self) -> int:
        """Get remaining seconds."""
        return self._remaining_seconds

    @property
    def elapsed_seconds(self) -> int:
        """Get elapsed seconds in current session."""
        return self._elapsed_seconds

    @property
    def work_sessions(self) -> int:
        """Get number of completed work sessions."""
        return self._work_sessions

    def start_work(self):
        """Start a work session."""
        self._state = PomodoroState.WORKING
        self._remaining_seconds = self.WORK_DURATION
        self._elapsed_seconds = 0
        self._start_time = datetime.now()
        self.on_state_change(self._state)

    def start_short_break(self):
        """Start a short break."""
        self._state = PomodoroState.SHORT_BREAK
        self._remaining_seconds = self.SHORT_BREAK_DURATION
        self._elapsed_seconds = 0
        self.on_state_change(self._state)

    def start_long_break(self):
        """Start a long break."""
        self._state = PomodoroState.LONG_BREAK
        self._remaining_seconds = self.LONG_BREAK_DURATION
        self._elapsed_seconds = 0
        self.on_state_change(self._state)

    def pause(self):
        """Pause the timer."""
        if self._state in (PomodoroState.WORKING, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK):
            self._state = PomodoroState.PAUSED
            self.on_state_change(self._state)

    def resume(self):
        """Resume the timer."""
        if self._state == PomodoroState.PAUSED:
            if self._elapsed_seconds < self._remaining_seconds:
                self._state = PomodoroState.WORKING if self._remaining_seconds <= self.WORK_DURATION else \
                    PomodoroState.SHORT_BREAK if self._remaining_seconds <= self.SHORT_BREAK_DURATION else \
                    PomodoroState.LONG_BREAK
            else:
                self._state = PomodoroState.IDLE
            self.on_state_change(self._state)

    def reset(self):
        """Reset the timer to initial state."""
        self._state = PomodoroState.IDLE
        self._remaining_seconds = self.WORK_DURATION
        self._elapsed_seconds = 0
        self._start_time = None
        self.on_state_change(self._state)

    def tick(self) -> bool:
        """
        Process one tick of the timer.

        Returns:
            True if timer completed, False otherwise
        """
        if self._state not in (PomodoroState.WORKING, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK):
            return False

        if self._remaining_seconds > 0:
            self._remaining_seconds -= 1
            self._elapsed_seconds += 1
            self.on_tick(self._remaining_seconds)
            return False
        else:
            # Timer completed
            if self._state == PomodoroState.WORKING:
                self._work_sessions += 1
            return True

    def get_duration(self) -> int:
        """Get current session duration."""
        if self._state == PomodoroState.WORKING:
            return self.WORK_DURATION
        elif self._state == PomodoroState.SHORT_BREAK:
            return self.SHORT_BREAK_DURATION
        elif self._state == PomodoroState.LONG_BREAK:
            return self.LONG_BREAK_DURATION
        return self.WORK_DURATION

    def get_actual_duration(self) -> int:
        """Get actual elapsed time in seconds."""
        return self._elapsed_seconds

    def get_start_time(self) -> Optional[datetime]:
        """Get session start time."""
        return self._start_time

    def get_end_time(self) -> datetime:
        """Get session end time."""
        return datetime.now()

    def format_time(self, seconds: int = None) -> str:
        """Format seconds to MM:SS string."""
        if seconds is None:
            seconds = self._remaining_seconds
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
