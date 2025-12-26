import os
import re
from pathlib import Path
from sqlalchemy import text, inspect
from src.db import engine

def is_postgresql():
    """Check if the database is PostgreSQL."""
    return engine.dialect.name == 'postgresql'

def is_sqlite():
    """Check if the database is SQLite."""
    return engine.dialect.name == 'sqlite'

def get_migration_files():
    """
    Get all migration SQL files sorted by their numeric prefix.
    
    Returns:
        List of migration file paths sorted by version number
    """
    migrations_dir = Path('migrations')
    if not migrations_dir.exists():
        return []
    
    migration_files = []
    for file_path in migrations_dir.glob('*.sql'):
        match = re.match(r'(\d+)_', file_path.name)
        if match:
            version = int(match.group(1))
            migration_files.append((version, file_path))
    
    return [path for _, path in sorted(migration_files)]

def run_migrations():
    """
    Execute all SQL migration files in order.
    Only runs migrations that haven't been applied yet.
    Migrations are executed in a transaction and rolled back on error.
    """
    check_migrations_table()
    applied_migrations = get_applied_migrations()
    
    migration_files = get_migration_files()
    
    if not migration_files:
        print("No migration files found in migrations/ directory")
        return
    
    print(f"Found {len(migration_files)} migration file(s)")
    
    pending_migrations = [f for f in migration_files if f.name not in applied_migrations]
    
    if not pending_migrations:
        print("All migrations are already applied")
        return
    
    print(f"Running {len(pending_migrations)} pending migration(s)")
    
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            for migration_file in pending_migrations:
                print(f"Running migration: {migration_file.name}")
                
                with open(migration_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                
                for statement in statements:
                    if not statement:
                        continue
                    
                    # Skip PostgreSQL-specific commands for SQLite
                    if is_sqlite():
                        # Skip CREATE EXTENSION (PostgreSQL only)
                        if 'CREATE EXTENSION' in statement.upper():
                            continue
                        # Skip uuid_generate_v4() function calls (PostgreSQL only)
                        if 'uuid_generate_v4()' in statement:
                            # Replace with SQLite-compatible random UUID generation
                            statement = statement.replace(
                                'uuid_generate_v4()',
                                "(lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6))))"
                            )
                        # Skip CREATE FUNCTION and TRIGGER (PostgreSQL-specific syntax)
                        if 'CREATE OR REPLACE FUNCTION' in statement.upper() or 'CREATE TRIGGER' in statement.upper():
                            continue
                        # Replace UUID type with TEXT for SQLite
                        statement = statement.replace('UUID', 'TEXT')
                    
                    try:
                        connection.execute(text(statement))
                    except Exception as e:
                        # For SQLite, some PostgreSQL-specific statements will fail
                        # Log but continue if it's a known incompatibility
                        if is_sqlite() and ('EXTENSION' in str(e) or 'FUNCTION' in str(e) or 'TRIGGER' in str(e)):
                            print(f"  Skipping PostgreSQL-specific statement for SQLite: {statement[:50]}...")
                            continue
                        raise
                
                mark_migration_applied(migration_file.name, connection)
                print(f"✓ Migration {migration_file.name} completed successfully")
            
            trans.commit()
            print("All pending migrations completed successfully")
        except Exception as e:
            trans.rollback()
            print(f"Migration failed: {e}")
            raise

def check_migrations_table():
    """
    Check if migrations tracking table exists, create if not.
    This allows tracking which migrations have been run.
    """
    with engine.connect() as connection:
        try:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(255) PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            connection.commit()
        except Exception as e:
            print(f"Error creating migrations table: {e}")

def get_applied_migrations():
    """
    Get list of already applied migrations from tracking table.
    
    Returns:
        Set of applied migration version strings
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version FROM schema_migrations"))
            return {row[0] for row in result}
    except Exception:
        return set()

def mark_migration_applied(version, connection=None):
    """
    Mark a migration as applied in the tracking table.
    
    Args:
        version: Migration version string (filename)
        connection: Optional existing connection to use (for transactions)
    """
    try:
        if is_postgresql():
            sql = "INSERT INTO schema_migrations (version) VALUES (:version) ON CONFLICT DO NOTHING"
        else:
            # SQLite doesn't support ON CONFLICT DO NOTHING in older versions, use INSERT OR IGNORE
            sql = "INSERT OR IGNORE INTO schema_migrations (version) VALUES (:version)"
        
        if connection:
            connection.execute(text(sql), {"version": version})
        else:
            with engine.connect() as conn:
                conn.execute(text(sql), {"version": version})
                conn.commit()
    except Exception as e:
        print(f"Error marking migration as applied: {e}")

