from datetime import datetime, timedelta

import pytest

from backend.services.farm_service import FarmService


@pytest.fixture
def farm(tmp_path):
    service = FarmService(db_path=tmp_path / "test.db")
    service.load()
    return service


def test_plant_and_harvest(farm):
    result = farm.plant(1, "trigo")
    assert result.ok is True
    assert farm.gold == 100 - 5

    plot = farm.get_plot(1)
    assert plot is not None
    past = datetime.now() - timedelta(seconds=10)
    plot.crop.restore_planted(past)

    harvest = farm.harvest(1)
    assert harvest.ok is True
    assert harvest.reward_gold == 10
    assert farm.gold == 100 - 5 + 10


def test_cannot_plant_on_occupied_plot(farm):
    farm.plant(1, "trigo")
    result = farm.plant(1, "maiz")
    assert result.ok is False


def test_not_enough_gold(farm):
    farm.gold = 0
    result = farm.plant(1, "trigo")
    assert result.ok is False
    assert "oro suficiente" in result.message


def test_persistence(tmp_path):
    db = tmp_path / "persist.db"

    svc1 = FarmService(db_path=db)
    svc1.load()
    svc1.plant(2, "zanahoria")
    gold_after_plant = svc1.gold

    svc2 = FarmService(db_path=db)
    svc2.load()
    assert svc2.gold == gold_after_plant
    assert svc2.get_plot(2).is_occupied() is True
    assert svc2.get_plot(2).semilla == "zanahoria"
