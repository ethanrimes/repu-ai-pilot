# scripts/setup/init_supabase.py
# Path: scripts/setup/init_supabase.py

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import click
from dotenv import load_dotenv

# Get paths relative to the script
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent  # Adjust based on your script location
backend_dir = project_root / 'backend'

# Add backend to path
sys.path.append(str(backend_dir))

# Load root .env first (base configuration)
root_env = project_root / '.env'
if root_env.exists():
    print(f"Loading root .env from: {root_env.absolute()}")
    load_dotenv(root_env)

# Load backend .env second (overrides root values)
backend_env = backend_dir / '.env'
if backend_env.exists():
    print(f"Loading backend .env from: {backend_env.absolute()}")
    load_dotenv(backend_env, override=True)  # override=True means backend values take precedence


load_dotenv()

class SupabaseInitializer:
    """Modular Supabase database initializer"""
    
    def __init__(self):
        # Load configuration from environment
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.database_url = os.getenv('DATABASE_URL')
        
        if not all([self.supabase_url, self.supabase_key, self.database_url]):
            raise ValueError("Missing Supabase credentials in .env file")
        
        self.db_params = self._parse_database_url(self.database_url)
        self.schema_dir = Path(__file__).parent.parent.parent / 'backend' / 'api' / 'database' / 'schemas'
    
    def _parse_database_url(self, url):
        """Parse PostgreSQL URL into connection parameters"""
        import re
        pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
        match = re.match(pattern, url)
        if match:
            return {
                'user': match.group(1),
                'password': match.group(2),
                'host': match.group(3),
                'port': match.group(4),
                'database': match.group(5)
            }
        raise ValueError("Invalid DATABASE_URL format")
    
    def _execute_sql_file(self, filename: str, description: str):
        """Execute SQL commands from a file"""
        sql_file = self.schema_dir / filename
        
        if not sql_file.exists():
            click.echo(f"  ⚠️  {filename} not found, skipping...")
            return
        
        click.echo(f"📋 {description}...")
        
        conn = psycopg2.connect(**self.db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        try:
            with open(sql_file, 'r') as f:
                sql_content = f.read()
                # Split by semicolon but not within functions
                statements = self._split_sql_statements(sql_content)
                
                for statement in statements:
                    if statement.strip():
                        try:
                            cur.execute(statement)
                            click.echo(f"  ✅ Executed: {statement[:50]}...")
                        except Exception as e:
                            if 'already exists' not in str(e):
                                click.echo(f"  ⚠️  Warning: {e}")
        
        except Exception as e:
            click.echo(f"  ❌ Error executing {filename}: {e}")
        finally:
            cur.close()
            conn.close()
    
    def _split_sql_statements(self, sql_content: str) -> list:
        """Split SQL content into individual statements"""
        # Simple splitter - can be enhanced for complex cases
        statements = []
        current = []
        in_function = False
        
        for line in sql_content.split('\n'):
            if 'CREATE OR REPLACE FUNCTION' in line or 'CREATE FUNCTION' in line:
                in_function = True
            
            current.append(line)
            
            if not in_function and line.strip().endswith(';'):
                statements.append('\n'.join(current))
                current = []
            elif in_function and line.strip() == '$$ language \'plpgsql\';':
                statements.append('\n'.join(current))
                current = []
                in_function = False
        
        if current:
            statements.append('\n'.join(current))
        
        return statements
    
    def initialize(self):
        """Run complete initialization"""
        click.echo("🚀 Initializing Supabase database...")
        click.echo("=" * 50)
        
        # Execute schema files in order
        self._execute_sql_file('tables.sql', 'Creating tables')
        self._execute_sql_file('indexes.sql', 'Creating indexes')
        self._execute_sql_file('functions.sql', 'Creating functions')
        self._execute_sql_file('triggers.sql', 'Creating triggers')
        
        click.echo("=" * 50)
        click.echo("✨ Supabase initialization complete!")
    
    def reset_database(self):
        """Drop and recreate all tables (WARNING: Destructive)"""
        if click.confirm("⚠️  This will DELETE all data. Are you sure?"):
            click.echo("🗑️ Dropping all tables...")
            
            conn = psycopg2.connect(**self.db_params)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            
            # Drop all tables in reverse dependency order
            tables = [
                'analytics_events',
                'conversation_messages',
                'sessions',
                'document_chunks',
                'documents',
                'order_items',
                'orders',
                'prices',
                'stock',
                'customers'
            ]
            
            for table in tables:
                try:
                    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    click.echo(f"  ✅ Dropped {table}")
                except Exception as e:
                    click.echo(f"  ❌ Error dropping {table}: {e}")
            
            cur.close()
            conn.close()
            
            # Reinitialize
            self.initialize()

@click.command()
@click.option('--reset', is_flag=True, help='Drop and recreate all tables')
def main(reset):
    """Initialize Supabase database"""
    try:
        initializer = SupabaseInitializer()
        
        if reset:
            initializer.reset_database()
        else:
            initializer.initialize()
            
    except Exception as e:
        click.echo(f"❌ Initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()