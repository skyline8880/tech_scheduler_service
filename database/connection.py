import psycopg

from core.secrets import DatabaseSecrets


class DatabaseConnection():
    async def __call__(self) -> psycopg.AsyncConnection:
        self.connect = await psycopg.AsyncConnection.connect(
            host=DatabaseSecrets.PGHOST,
            dbname=DatabaseSecrets.PGDATABASE,
            user=DatabaseSecrets.PGUSERNAME,
            password=DatabaseSecrets.PGPASSWORD,
            port=DatabaseSecrets.PGPORT
        )
        return self.connect


CreateConnection = DatabaseConnection()
