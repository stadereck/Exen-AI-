from __future__ import annotations
import aiosqlite
from pathlib import Path
from typing import Any, Iterable, Optional

from config.config import BotConfig

class Database:
    def __init__(self, path: str = BotConfig.DATABASE_PATH) -> None:
        self.path = Path(path)
        self.connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = await aiosqlite.connect(self.path)
        self.connection.row_factory = aiosqlite.Row
        await self.create_tables()

    async def create_tables(self) -> None:
        assert self.connection is not None

        await self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS bot_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS giveaways (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                prize TEXT NOT NULL,
                ends_at TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                winner_id INTEGER
            );

            CREATE TABLE IF NOT EXISTS giveaway_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                giveaway_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                UNIQUE(giveaway_id, user_id)
            );

            CREATE TABLE IF NOT EXISTS polls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        await self.connection.commit()

    async def execute(self, query: str, parameters: Iterable[Any] = ()) -> int:
        assert self.connection is not None
        cursor = await self.connection.execute(query, tuple(parameters))
        await self.connection.commit()
        return cursor.lastrowid

    async def fetchone(self, query: str, parameters: Iterable[Any] = ()) -> Optional[aiosqlite.Row]:
        assert self.connection is not None
        cursor = await self.connection.execute(query, tuple(parameters))
        row = await cursor.fetchone()
        await cursor.close()
        return row

    async def fetchall(self, query: str, parameters: Iterable[Any] = ()) -> list[aiosqlite.Row]:
        assert self.connection is not None
        cursor = await self.connection.execute(query, tuple(parameters))
        rows = await cursor.fetchall()
        await cursor.close()
        return rows

    async def get_config(self, key: str, default: Any = None) -> Any:
        row = await self.fetchone("SELECT value FROM bot_config WHERE key = ?", (key,))
        return row["value"] if row is not None else default

    async def set_config(self, key: str, value: str) -> None:
        await self.execute(
            "INSERT INTO bot_config (key, value) VALUES (?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value = excluded.value;",
            (key, value),
        )

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None
