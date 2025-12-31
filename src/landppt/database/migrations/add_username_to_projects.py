"""
Database migration script to add username column to projects table

This migration adds a username field to the projects table to associate
projects with their owners.
"""

import asyncio
import logging
from sqlalchemy import Column, String, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from ..models import Base, Project
from ...core.config import database_config

logger = logging.getLogger(__name__)


async def add_username_column():
    """Add username column to projects table"""
    engine = create_async_engine(database_config.database_url)
    
    async with engine.connect() as conn:
        # Check if username column already exists
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'username'
        """))
        
        if result.fetchone():
            logger.info("username column already exists in projects table")
            return
        
        # Add username column
        logger.info("Adding username column to projects table...")
        await conn.execute(text("""
            ALTER TABLE projects 
            ADD COLUMN username VARCHAR(50) NOT NULL DEFAULT 'admin'
        """))
        
        # Create index on username column
        logger.info("Creating index on username column...")
        await conn.execute(text("""
            CREATE INDEX idx_projects_username ON projects(username)
        """))
        
        await conn.commit()
        logger.info("Successfully added username column and index")


async def update_existing_projects():
    """Update existing projects with default username"""
    engine = create_async_engine(database_config.database_url)
    
    async with engine.connect() as conn:
        # Update existing projects
        logger.info("Updating existing projects with default username...")
        result = await conn.execute(text("""
            UPDATE projects 
            SET username = 'admin' 
            WHERE username IS NULL OR username = ''
        """))
        
        await conn.commit()
        logger.info(f"Updated {result.rowcount} projects with default username")


async def verify_migration():
    """Verify the migration was successful"""
    engine = create_async_engine(database_config.database_url)
    
    async with engine.connect() as conn:
        # Check if username column exists
        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'projects' AND column_name = 'username'
        """))
        
        column_info = result.fetchone()
        if column_info:
            logger.info(f"Username column verified: {column_info}")
        else:
            raise Exception("Username column not found after migration")
        
        # Check if index exists
        result = await conn.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'projects' AND indexname = 'idx_projects_username'
        """))
        
        if result.fetchone():
            logger.info("Username index verified")
        else:
            logger.warning("Username index not found")


async def run_migration():
    """Run the complete migration"""
    try:
        logger.info("Starting database migration: Add username to projects table")
        
        # Add username column
        await add_username_column()
        
        # Update existing projects
        await update_existing_projects()
        
        # Verify migration
        await verify_migration()
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run migration
    asyncio.run(run_migration())