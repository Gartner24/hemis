"""
Database Connection Manager for HEMIS
Handles role-based database connections to the same database with different user permissions
"""

import os
import pymysql
from pymysql.cursors import DictCursor
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    """Manages database connections for different user roles to the same database"""
    
    def __init__(self):
        self.connections = {}
        self.role_db_mapping = self._parse_role_db_mapping()
        
    def _parse_role_db_mapping(self) -> Dict[str, str]:
        """Parse the role to database mapping from environment variables"""
        mapping_str = os.getenv('ROLE_DB_MAPPING', '')
        mapping = {}
        
        for item in mapping_str.split(','):
            if ':' in item:
                role, db = item.strip().split(':', 1)
                mapping[role] = db.strip()
                
        return mapping
    
    def get_connection_config(self, role: str) -> Dict[str, Any]:
        """Get database connection configuration for a specific role"""
        role_upper = role.upper().replace(' ', '_')
        
        # All roles connect to the same database (hemis_db) but with different users
        db_name = self.role_db_mapping.get(role, 'hemis_db')
        
        # Get the specific user credentials for this role
        user_key = f'{role_upper}_DB_USER'
        password_key = f'{role_upper}_DB_PASSWORD'
        
        # Fallback to main database user if role-specific user not found
        db_user = os.getenv(user_key, os.getenv('DB_USER', 'hemis_user'))
        db_password = os.getenv(password_key, os.getenv('DB_PASSWORD', ''))
        
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'database': db_name,
            'user': db_user,
            'password': db_password,
            'charset': 'utf8mb4',
            'cursorclass': DictCursor,
            'autocommit': True,
            'connect_timeout': 10,
            'read_timeout': 30,
            'write_timeout': 30
        }
        
        return config
    
    def get_connection(self, role: str) -> pymysql.Connection:
        """Get a database connection for a specific role"""
        try:
            config = self.get_connection_config(role)
            connection = pymysql.connect(**config)
            
            # Test the connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                
            logger.debug(f"Database connection established for role: {role} using user: {config['user']}")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to connect to database for role {role}: {str(e)}")
            raise
    
    def get_connection_pool(self, role: str, pool_size: int = 5) -> list:
        """Get a connection pool for a specific role"""
        pool = []
        try:
            for _ in range(pool_size):
                conn = self.get_connection(role)
                pool.append(conn)
            logger.info(f"Connection pool created for role {role} with {pool_size} connections")
            return pool
        except Exception as e:
            logger.error(f"Failed to create connection pool for role {role}: {str(e)}")
            raise
    
    def close_connection(self, connection: pymysql.Connection):
        """Close a database connection"""
        try:
            if connection and connection.open:
                connection.close()
                logger.debug("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")
    
    def close_all_connections(self):
        """Close all active connections"""
        for role, connections in self.connections.items():
            if isinstance(connections, list):
                for conn in connections:
                    self.close_connection(conn)
            else:
                self.close_connection(connections)
        self.connections.clear()
        logger.info("All database connections closed")
    
    def execute_query(self, role: str, query: str, params: Optional[tuple] = None) -> list:
        """Execute a query for a specific role"""
        connection = None
        try:
            connection = self.get_connection(role)
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    connection.commit()
                    return [{'affected_rows': cursor.rowcount}]
        except Exception as e:
            logger.error(f"Query execution failed for role {role}: {str(e)}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                self.close_connection(connection)
    
    def execute_transaction(self, role: str, queries: list) -> bool:
        """Execute multiple queries in a transaction for a specific role"""
        connection = None
        try:
            connection = self.get_connection(role)
            connection.begin()
            
            with connection.cursor() as cursor:
                for query, params in queries:
                    cursor.execute(query, params or ())
            
            connection.commit()
            logger.info(f"Transaction completed successfully for role {role}")
            return True
            
        except Exception as e:
            logger.error(f"Transaction failed for role {role}: {str(e)}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection:
                self.close_connection(connection)

# Global instance
db_manager = DatabaseConnectionManager()

def get_db_connection(role: str) -> pymysql.Connection:
    """Get a database connection for a specific role"""
    return db_manager.get_connection(role)

def execute_query(role: str, query: str, params: Optional[tuple] = None) -> list:
    """Execute a query for a specific role"""
    return db_manager.execute_query(role, query, params)

def execute_transaction(role: str, queries: list) -> bool:
    """Execute multiple queries in a transaction for a specific role"""
    return db_manager.execute_transaction(role, queries)

def close_db_connection(connection: pymysql.Connection):
    """Close a database connection"""
    db_manager.close_connection(connection)

def close_all_db_connections():
    """Close all database connections"""
    db_manager.close_all_connections()
