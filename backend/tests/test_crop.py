from datetime import datetime, timedelta

from backend.cropsystem.crops import Crop


def test_crop_plant_harvest_cycle():
    crop = Crop("Trigo", 5, 10)
    t0 = datetime(2026, 1, 1, 12, 0, 0)

    assert crop.plant() is True
    crop.restore_planted(t0)

    assert crop.is_growing is True
    assert crop.is_ready(now=t0 + timedelta(seconds=4)) is False
    assert crop.is_ready(now=t0 + timedelta(seconds=5)) is True

    reward = crop.harvest(now=t0 + timedelta(seconds=5))
    assert reward == 10
    assert crop.is_idle is True


def test_restore_planted():
    crop = Crop("Maíz", 10, 20)
    started = datetime(2026, 1, 1, 8, 0, 0)
    crop.restore_planted(started)

    assert crop.is_growing is True
    assert crop.time_remaining(now=started + timedelta(seconds=3)) == 7.0
