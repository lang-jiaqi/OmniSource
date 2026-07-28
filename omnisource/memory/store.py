"""SQLite memory of signals we've already reported, per track.

The radar runs every day over an overlapping time window, so the same paper
shows up on several consecutive runs. Without memory it would land in the
briefing again and again. Dedup is per track — the same paper may legitimately
appear in two different tracks' reports — so the key is (id, track).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from ..models import Signal


class SignalStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create the table, recreating an older track-unaware one if found.
        The DB is a disposable cache, so dropping it just resets dedup history."""
        cols = {row[1] for row in self.conn.execute("PRAGMA table_info(reported_signals)")}
        if cols and "track" not in cols:
            self.conn.execute("DROP TABLE reported_signals")
            cols = set()
        if not cols:
            self.conn.execute(
                "CREATE TABLE reported_signals ("
                "  id TEXT,"
                "  track TEXT,"
                "  title TEXT,"
                "  first_reported TEXT,"  # the date we first put it in a briefing
                "  sources TEXT,"
                "  type TEXT,"
                "  topic TEXT,"
                "  final_score REAL,"
                "  PRIMARY KEY (id, track)"
                ")"
            )
        self.conn.commit()

    def seen_ids(self, track: str) -> set[str]:
        rows = self.conn.execute("SELECT id FROM reported_signals WHERE track = ?", (track,))
        return {row[0] for row in rows}

    def filter_unseen(self, signals: list[Signal], track: str) -> list[Signal]:
        """Drop signals already reported for this track on an earlier run."""
        seen = self.seen_ids(track)
        return [s for s in signals if s.id not in seen]

    def record(self, signals: list[Signal], date: str, track: str) -> None:
        """Mark signals as reported for this track. INSERT OR IGNORE keeps the first date."""
        self.conn.executemany(
            "INSERT OR IGNORE INTO reported_signals "
            "(id, track, title, first_reported, sources, type, topic, final_score) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (s.id, track, s.title, date, ",".join(s.sources), s.type, s.topic, s.final_score)
                for s in signals
            ],
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
