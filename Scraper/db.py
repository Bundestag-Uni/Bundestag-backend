import psycopg2
from psycopg2 import sql

class PostgresDatabase:
    def __init__(self, host, database, user, password, port=5432):
            self.connection = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )

    def execute_query(self, query, params=None):
        """
        Execute a query on the database.

        :param query: The SQL query to execute
        :param params: Optional parameters for the query
        :return: Query result for SELECT statements, None otherwise
        """
        if self.connection is None:
            print("Database is not connected.")
            return None

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().lower().startswith("select"):
                    result = cursor.fetchall()
                    return result
                else:
                    self.connection.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()

    def has_rows(self, tablename):

        if self.connection is None:
            print("Database is not connected.")
            return None
        
        try:
            with self.connection.cursor() as cursor:
                query = sql.SQL("SELECT EXISTS (SELECT 1 FROM {table} LIMIT 1);").format(
                    table=sql.Identifier(tablename)
                )
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0]  # True if rows exist, False otherwise
        except Exception as e:
            print(f"Error checking rows in table '{tablename}': {e}")
            return False
