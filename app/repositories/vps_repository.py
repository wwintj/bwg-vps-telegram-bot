import aiosqlite
from app.config import DATABASE_PATH


class VpsRepository:
    @staticmethod
    async def add_vps(
        name: str,
        veid: str,
        api_key: str,
        ssh_port: str = "22",
        note: str = "",
        expiry_date: str = "",
    ):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "INSERT INTO vps_instances (name, veid, api_key, ssh_port, note, expiry_date) VALUES (?, ?, ?, ?, ?, ?)",
                (name, veid, api_key, ssh_port, note, expiry_date),
            )
            await db.commit()

    @staticmethod
    async def get_all_vps():
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM vps_instances ORDER BY id ASC") as cursor:
                return [dict(row) for row in await cursor.fetchall()]

    @staticmethod
    async def get_vps(vps_id: int):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM vps_instances WHERE id = ?", (vps_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    @staticmethod
    async def delete_vps(vps_id: int):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("DELETE FROM vps_instances WHERE id = ?", (vps_id,))
            await db.commit()
