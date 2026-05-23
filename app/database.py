import os
import aiosqlite
import logging
from app.config import Config

logger = logging.getLogger(__name__)

async def init_db():
    """Initialize the SQLite database and create necessary tables."""
    db_path = Config.DATABASE_PATH
    db_dir = os.path.dirname(db_path)
    
    # Ensure the data directory exists
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS vps_instances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    veid TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    ssh_port INTEGER DEFAULT 22,
                    note TEXT,
                    expiry_date TEXT
                )
            ''')
            await db.commit()
            logger.info(f"Database initialized successfully at {db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
