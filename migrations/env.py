"""Alembic Environment Configuration

This file runs when you execute migration commands.
It connects to your database and compares your SQLAlchemy models with the actual database schema.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add the app directory to Python path so we can import models
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import your Flask app and models
from app import create_app
from app.extensions import db
from app import models  # This imports all models

# Create Flask app to get database configuration
app = create_app()

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# IMPORTANT: This is where Alembic learns about your models
# target_metadata tells Alembic what the database SHOULD look like
target_metadata = db.metadata

# Override the database URL from app config (uses .env)
config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    
    This generates SQL scripts without connecting to database.
    Useful for generating SQL to run manually.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    
    This connects to the database and applies migrations directly.
    This is what you'll use 99% of the time.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Compare types to detect column type changes
            compare_type=True,
            # Compare server defaults
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine which mode to run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
