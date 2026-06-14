import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'healthy_life_secret_key_987654321_abc')
    
    # MySQL Database configurations
    MYSQL_HOST = os.environ.get('DB_HOST', 'localhost')
    MYSQL_USER = os.environ.get('DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', '')
    MYSQL_DB = os.environ.get('DB_NAME', 'healthy_life_db')
    MYSQL_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # Path for SQLite fallback database in case MySQL is unavailable
    SQLITE_DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'healthy_life.db')
