from datetime import datetime, timedelta

import pytest

from backend.timed_action import TimedAction


def test_start_and_finish():
    action = TimedAction(duration_seconds=5.0)
    t0 = datetime(2026, 1, 1, 12, 0, 0)

    assert action.start(when=t0) is True
    assert action.is_active(now=t0) is True
    assert action.is_ready(now=t0) is False

    t_done = t0 + timedelta(seconds=5)
    assert action.is_ready(now=t_done) is True
    assert action.finish_if_ready(now=t_done) is True
    assert action.is_idle is True


def test_start_twice_returns_false():
    action = TimedAction(duration_seconds=5.0)
    assert action.start() is True
    assert action.start() is False


def test_progress_ratio():
    action = TimedAction(duration_seconds=10.0)
    t0 = datetime(2026, 1, 1, 12, 0, 0)
    action.start(when=t0)

    assert action.progress_ratio(now=t0) == 0.0
    assert action.progress_ratio(now=t0 + timedelta(seconds=5)) == 0.5
    assert action.progress_ratio(now=t0 + timedelta(seconds=10)) == 1.0
