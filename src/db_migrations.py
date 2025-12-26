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

def column_exists(connection, table_name, column_name):
    """Check if a column exists in a table (SQLite only)."""
    if not is_sqlite():
        return False
    
    try:
        result = connection.execute(text(f"PRAGMA table_info({table_name})"))
        columns = [row[1] for row in result]  # Column name is at index 1
        return column_name.lower() in [col.lower() for col in columns]
    except Exception:
        return False

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
                        
                        # Process ALTER TABLE ADD COLUMN statements for SQLite
                        # SQLite doesn't support IF NOT EXISTS in ALTER TABLE ADD COLUMN
                        if 'ALTER TABLE' in statement.upper() and 'ADD COLUMN' in statement.upper():
                            # Extract table name
                            table_name_match = re.search(r'ALTER TABLE\s+(\w+)', statement, re.IGNORECASE)
                            if table_name_match:
                                table_name = table_name_match.group(1)
                                
                                # Remove IF NOT EXISTS from the statement
                                statement_no_if = re.sub(r'\s+IF\s+NOT\s+EXISTS\s+', ' ', statement, flags=re.IGNORECASE)
                                
                                # Split by ", ADD COLUMN" to separate multiple ADD COLUMN clauses
                                # But preserve the ALTER TABLE part for the first one
                                parts = re.split(r',\s*ADD\s+COLUMN\s+', statement_no_if, flags=re.IGNORECASE)
                                
                                if len(parts) > 1:
                                    # Multiple ADD COLUMN clauses - process each separately
                                    # First part: "ALTER TABLE table_name ADD COLUMN col1 def1"
                                    first_part = parts[0]
                                    first_col_match = re.search(r'ADD\s+COLUMN\s+(\w+)\s+(.+)', first_part, re.IGNORECASE | re.DOTALL)
                                    if first_col_match:
                                        col_name = first_col_match.group(1)
                                        col_def = first_col_match.group(2).strip().rstrip(',')
                                        if not column_exists(connection, table_name, col_name):
                                            try:
                                                connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"))
                                            except Exception as e:
                                                if 'duplicate column name' not in str(e).lower():
                                                    raise
                                                print(f"  Column {col_name} already exists in {table_name}, skipping...")
                                        
                                    # Remaining parts: "col2 def2", "col3 def3", etc.
                                    for part in parts[1:]:
                                        # Remove trailing comma and semicolon
                                        part = part.strip().rstrip(';').rstrip(',')
                                        col_match = re.match(r'(\w+)\s+(.+)', part, re.DOTALL)
                                        if col_match:
                                            col_name = col_match.group(1)
                                            col_def = col_match.group(2).strip()
                                            if not column_exists(connection, table_name, col_name):
                                                try:
                                                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"))
                                                except Exception as e:
                                                    if 'duplicate column name' not in str(e).lower():
                                                        raise
                                                    print(f"  Column {col_name} already exists in {table_name}, skipping...")
                                    
                                    # Skip the original statement since we processed it separately
                                    continue
                                else:
                                    # Single ADD COLUMN - remove IF NOT EXISTS and check before executing
                                    single_match = re.search(r'ADD\s+COLUMN\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', statement, re.IGNORECASE)
                                    if single_match:
                                        col_name = single_match.group(1)
                                        if column_exists(connection, table_name, col_name):
                                            print(f"  Column {col_name} already exists in {table_name}, skipping...")
                                            continue
                                        # Remove IF NOT EXISTS for single column case
                                        statement = statement_no_if
                    
                    try:
                        connection.execute(text(statement))
                    except Exception as e:
                        # For SQLite, handle duplicate column errors gracefully
                        if is_sqlite() and ('duplicate column name' in str(e).lower() or 'already exists' in str(e).lower()):
                            print(f"  Column already exists, skipping: {statement[:50]}...")
                            continue
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

