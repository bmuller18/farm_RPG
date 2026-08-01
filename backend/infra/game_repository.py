"""Persistencia SQLite del estado del juego."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from backend.domain.plot import Plot
except ImportError:
    from domain.plot import Plot

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "farm_rpg.db"

DEFAULT_PLAYER_ID = 1
DEFAULT_PLAYER_NAME = "Jugador"
STARTING_GOLD = 100
NUM_PLOTS = 3


class GameRepository:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS player (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL DEFAULT 'Jugador',
                    money INTEGER NOT NULL DEFAULT 100,
                    level INTEGER NOT NULL DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS plots (
                    player_id INTEGER NOT NULL,
                    slot INTEGER NOT NULL,
                    semilla TEXT,
                    crop_name TEXT,
                    grow_seconds REAL,
                    reward_gold INTEGER,
                    started_at TEXT,
                    PRIMARY KEY (player_id, slot),
                    FOREIGN KEY (player_id) REFERENCES player(id)
                );
                """
            )

    def get_or_create_player(
        self,
        player_id: int = DEFAULT_PLAYER_ID,
        name: str = DEFAULT_PLAYER_NAME,
        starting_gold: int = STARTING_GOLD,
    ) -> dict:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, money, level FROM player WHERE id = ?",
                (player_id,),
            ).fetchone()

            if row is None:
                conn.execute(
                    "INSERT INTO player (id, name, money) VALUES (?, ?, ?)",
                    (player_id, name, starting_gold),
                )
                return {
                    "id": player_id,
                    "name": name,
                    "money": starting_gold,
                    "level": 1,
                }

            return dict(row)

    def save_player(
        self,
        player_id: int,
        name: str,
        money: int,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE player SET name = ?, money = ? WHERE id = ?",
                (name, money, player_id),
            )

    def load_plots(self, player_id: int) -> dict[int, Optional[dict]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT slot, semilla, crop_name, grow_seconds, reward_gold, started_at
                FROM plots
                WHERE player_id = ?
                """,
                (player_id,),
            ).fetchall()

        saved: dict[int, Optional[dict]] = {slot: None for slot in range(1, NUM_PLOTS + 1)}
        for row in rows:
            if row["started_at"] is None:
                saved[row["slot"]] = None
                continue
            saved[row["slot"]] = {
                "semilla": row["semilla"],
                "crop_name": row["crop_name"],
                "grow_seconds": row["grow_seconds"],
                "reward_gold": row["reward_gold"],
                "started_at": row["started_at"],
            }
        return saved

    def save_plot(self, player_id: int, slot: int, plot: Plot) -> None:
        with self._connect() as conn:
            if not plot.is_occupied() or plot.crop is None:
                conn.execute(
                    """
                    INSERT INTO plots (player_id, slot, semilla, crop_name, grow_seconds, reward_gold, started_at)
                    VALUES (?, ?, NULL, NULL, NULL, NULL, NULL)
                    ON CONFLICT(player_id, slot) DO UPDATE SET
                        semilla = NULL,
                        crop_name = NULL,
                        grow_seconds = NULL,
                        reward_gold = NULL,
                        started_at = NULL
                    """,
                    (player_id, slot),
                )
                return

            crop = plot.crop
            started_at = crop.started_at
            if started_at is None:
                return

            conn.execute(
                """
                INSERT INTO plots (player_id, slot, semilla, crop_name, grow_seconds, reward_gold, started_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(player_id, slot) DO UPDATE SET
                    semilla = excluded.semilla,
                    crop_name = excluded.crop_name,
                    grow_seconds = excluded.grow_seconds,
                    reward_gold = excluded.reward_gold,
                    started_at = excluded.started_at
                """,
                (
                    player_id,
                    slot,
                    plot.semilla,
                    crop.name,
                    crop.grow_seconds,
                    crop.reward,
                    started_at.isoformat(),
                ),
            )

    def save_all_plots(self, player_id: int, plots: dict[int, Plot]) -> None:
        for slot, plot in plots.items():
            self.save_plot(player_id, slot, plot)
