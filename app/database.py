import os
import aiosqlite
import logging
from app.config import Config

logger = logging.getLogger(__name__)

async def init_db():
    """Initialize the SQLite database and handle smooth schema migrations."""
    db_path = Config.DATABASE_PATH
    db_dir = os.path.dirname(db_path)
    
    # Ensure the data directory exists
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    try:
        async with aiosqlite.connect(db_path) as db:
            # 1. Create table with full schema if it doesn't exist (for fresh installs)
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
            
            # 2. Check existing columns to support smooth upgrades for older databases
            cursor = await db.execute("PRAGMA table_info(vps_instances)")
            columns_info = await cursor.fetchall()
            existing_columns = [col[1] for col in columns_info]
            
            # 3. Add missing columns safely without losing data
            if 'ssh_port' not in existing_columns:
                await db.execute("ALTER TABLE vps_instances ADD COLUMN ssh_port INTEGER DEFAULT 22")
                logger.info("Database upgraded: Added missing 'ssh_port' column.")
                
            if 'note' not in existing_columns:
                await db.execute("ALTER TABLE vps_instances ADD COLUMN note TEXT")
                logger.info("Database upgraded: Added missing 'note' column.")
                
            if 'expiry_date' not in existing_columns:
                await db.execute("ALTER TABLE vps_instances ADD COLUMN expiry_date TEXT")
                logger.info("Database upgraded: Added missing 'expiry_date' column.")

            await db.commit()
            logger.info(f"Database initialized and verified successfully at {db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
