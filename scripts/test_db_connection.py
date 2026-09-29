import sys
import os
import time

# Add the parent directory to sys.path so we can import from backend
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from backend.app.core.config import settings
from sqlalchemy import create_engine, text

def test_connection():
    print(f"Testing connection to: {settings.MYSQL_HOST}:{settings.MYSQL_PORT} / {settings.MYSQL_DATABASE}")
    engine = create_engine(settings.DATABASE_URL)
    max_retries = 30
    for i in range(max_retries):
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                print("Successfully connected to the database!")
                print(f"Result: {result.scalar()}")
                return
        except Exception as e:
            print(f"Attempt {i+1}/{max_retries} failed. Retrying in 2 seconds...")
            time.sleep(2)
    
    print("Failed to connect to the database after multiple attempts.")
    sys.exit(1)

if __name__ == "__main__":
    test_connection()
