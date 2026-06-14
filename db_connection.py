import os
import sys
import sqlite3
from config import Config

# Try to use PyMySQL as a drop-in replacement for MySQLdb
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    import MySQLdb
    HAS_MYSQL_DRIVER = True
except ImportError:
    HAS_MYSQL_DRIVER = False

class DBConnectionManager:
    def __init__(self):
        self.use_sqlite = True
        self.error_msg = None
        self.conn_config = {
            'host': Config.MYSQL_HOST,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'db': Config.MYSQL_DB,
            'port': Config.MYSQL_PORT
        }
        
    def check_mysql_connection(self):
        """Attempts to connect to MySQL. Returns True if successful, False otherwise."""
        if not HAS_MYSQL_DRIVER:
            self.error_msg = "MySQL driver (PyMySQL/MySQLdb) is not installed."
            print("DB ERROR:", self.error_msg)
            return False
        
        try:
            # First, attempt connection to MySQL server without database to check if MySQL is running
            conn = MySQLdb.connect(
                host=self.conn_config['host'],
                user=self.conn_config['user'],
                password=self.conn_config['password'],
                port=self.conn_config['port'],
                connect_timeout=3
            )
            
            # Create database if it doesn't exist
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.conn_config['db']}")
            cursor.close()
            conn.close()
            
            # Test connection to the actual database
            conn = MySQLdb.connect(
                host=self.conn_config['host'],
                user=self.conn_config['user'],
                password=self.conn_config['password'],
                db=self.conn_config['db'],
                port=self.conn_config['port'],
                connect_timeout=3
            )
            conn.close()
            self.use_sqlite = False
            self.error_msg = None
            print("DB STATUS: Successfully connected to MySQL database.")
            return True
        except Exception as e:
            self.error_msg = str(e)
            print(f"DB WARNING: MySQL connection failed: {e}. Falling back to SQLite.")
            self.use_sqlite = True
            return False

    def init_db(self):
        """Initializes tables for either MySQL or SQLite based on connection status."""
        self.check_mysql_connection()
        
        if self.use_sqlite:
            # Initialize SQLite Database
            print("DB STATUS: Initializing SQLite local database.")
            conn = sqlite3.connect(Config.SQLITE_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_profile (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    age INTEGER NOT NULL,
                    gender TEXT NOT NULL,
                    height REAL NOT NULL,
                    weight REAL NOT NULL,
                    activity_level TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)
            conn.commit()
            conn.close()
        else:
            # Initialize MySQL Database
            conn = MySQLdb.connect(
                host=self.conn_config['host'],
                user=self.conn_config['user'],
                password=self.conn_config['password'],
                db=self.conn_config['db'],
                port=self.conn_config['port']
            )
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_profile (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL UNIQUE,
                    age INT NOT NULL,
                    gender VARCHAR(50) NOT NULL,
                    height FLOAT NOT NULL,
                    weight FLOAT NOT NULL,
                    activity_level VARCHAR(100) NOT NULL,
                    goal VARCHAR(100) NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)
            conn.commit()
            conn.close()

    def get_connection(self):
        """Returns raw database connection based on active engine."""
        if self.use_sqlite:
            conn = sqlite3.connect(Config.SQLITE_DB_PATH)
            # Enable foreign key support in SQLite
            conn.execute("PRAGMA foreign_keys = ON")
            # Set row factory to return dict-like rows
            conn.row_factory = sqlite3.Row
            return conn
        else:
            import MySQLdb
            # Import cursor class that returns results as dictionaries
            from MySQLdb.cursors import DictCursor
            return MySQLdb.connect(
                host=self.conn_config['host'],
                user=self.conn_config['user'],
                password=self.conn_config['password'],
                db=self.conn_config['db'],
                port=self.conn_config['port'],
                cursorclass=DictCursor
            )

    def execute_query(self, query, params=(), is_select=False, fetch_one=False):
        """Executes a query and handles connection, commits, and returns."""
        # Convert query placeholders from %s (MySQL) to ? (SQLite) if necessary
        if self.use_sqlite:
            query = query.replace('%s', '?')
            
        conn = self.get_connection()
        cursor = conn.cursor()
        result = None
        
        try:
            cursor.execute(query, params)
            if is_select:
                if fetch_one:
                    row = cursor.fetchone()
                    if row:
                        result = dict(row)
                else:
                    result = [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                result = cursor.lastrowid if not self.use_sqlite else cursor.lastrowid
        except Exception as e:
            print(f"QUERY ERROR: Query failed: {query}. Error: {e}")
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
        return result

    # --- Convenience DB Operations ---
    
    def get_user_by_email(self, email):
        query = "SELECT * FROM users WHERE email = %s"
        return self.execute_query(query, (email,), is_select=True, fetch_one=True)
        
    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE id = %s"
        return self.execute_query(query, (user_id,), is_select=True, fetch_one=True)

    def create_user(self, name, email, password_hash):
        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        return self.execute_query(query, (name, email, password_hash))

    def get_health_profile(self, user_id):
        query = "SELECT * FROM health_profile WHERE user_id = %s"
        return self.execute_query(query, (user_id,), is_select=True, fetch_one=True)

    def save_health_profile(self, user_id, age, gender, height, weight, activity_level, goal):
        # Check if profile exists
        existing = self.get_health_profile(user_id)
        if existing:
            query = """
                UPDATE health_profile 
                SET age = %s, gender = %s, height = %s, weight = %s, activity_level = %s, goal = %s
                WHERE user_id = %s
            """
            return self.execute_query(query, (age, gender, height, weight, activity_level, goal, user_id))
        else:
            query = """
                INSERT INTO health_profile (user_id, age, gender, height, weight, activity_level, goal)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            return self.execute_query(query, (user_id, age, gender, height, weight, activity_level, goal))

# Instantiate a global database manager
db_manager = DBConnectionManager()
