import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "modbot.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS config (
                guild_id INTEGER PRIMARY KEY,
                log_channel INTEGER,
                mute_role_id INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS muted_users (
                guild_id INTEGER,
                user_id INTEGER,
                role_id INTEGER,
                until TEXT,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        await db.commit()

async def add_warn(guild_id, user_id, mod_id, reason):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO warns (guild_id, user_id, moderator_id, reason) VALUES (?, ?, ?, ?)",
            (guild_id, user_id, mod_id, reason)
        )
        await db.commit()

async def get_warns(guild_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM warns WHERE guild_id = ? AND user_id = ? ORDER BY timestamp DESC",
            (guild_id, user_id)
        )
        return await cursor.fetchall()

async def clear_warns(guild_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM warns WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id)
        )
        await db.commit()

async def set_config(guild_id, log_channel=None, mute_role_id=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO config (guild_id, log_channel, mute_role_id)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
                log_channel = COALESCE(?, log_channel),
                mute_role_id = COALESCE(?, mute_role_id)
        """, (guild_id, log_channel, mute_role_id, log_channel, mute_role_id))
        await db.commit()

async def get_config(guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM config WHERE guild_id = ?", (guild_id,))
        return await cursor.fetchone()