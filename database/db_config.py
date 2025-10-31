import mysql.connector
from mysql.connector import Error
import os
import logging

logging.basicConfig(level=logging.INFO)

class Database:
    def __init__(self):
        self.connection = None

    def connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'fcp@123'),  # Your MySQL password
                database=os.getenv('DB_NAME', 'smartcareer')
            )
            if self.connection.is_connected():
                logging.info("✅ Successfully connected to database")
                return self.connection
        except Error as e:
            logging.error(f"❌ Database connection error: {e}")
            return None

    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("🔒 Database connection closed")

    def execute_query(self, query, params=None):
        """Execute a query"""
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Error as e:
            logging.error(f"⚠️ Query execution error: {e}")
            return None

    def fetch_all(self, query, params=None):
        """Fetch all results"""
        cursor = self.execute_query(query, params)
        if cursor:
            result = cursor.fetchall()
            cursor.close()
            return result
        return []

    def fetch_one(self, query, params=None):
        """Fetch single result"""
        cursor = self.execute_query(query, params)
        if cursor:
            result = cursor.fetchone()
            cursor.close()
            return result
        return None
