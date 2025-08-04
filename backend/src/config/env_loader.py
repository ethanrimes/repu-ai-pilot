from pathlib import Path
from dotenv import load_dotenv
import os

def load_environment():
    """Load environment variables in the correct order"""
    # Get the backend directory
    backend_dir = Path(__file__).parent.parent.parent
    project_root = backend_dir.parent
    
    # Load root .env first (base configuration)
    root_env = project_root / '.env'
    if root_env.exists():
        load_dotenv(root_env)
    
    # Load backend .env second (overrides root values)
    backend_env = backend_dir / '.env'
    if backend_env.exists():
        load_dotenv(backend_env, override=True)
    
    # Load environment-specific .env file (e.g., .env.production)
    env = os.getenv('ENVIRONMENT', 'development')
    env_file = backend_dir / f'.env.{env}'
    if env_file.exists():
        load_dotenv(env_file, override=True)

# Auto-load when module is imported
load_environment()