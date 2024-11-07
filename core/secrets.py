import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class DatabaseSecrets:
    PGHOST = os.getenv('PGHOST')
    PGDATABASE = os.getenv('PGDATABASE')
    PGUSERNAME = os.getenv('PGUSERNAME')
    PGPASSWORD = os.getenv('PGPASSWORD')
    PGPORT = os.getenv('PGPORT')
    SCHEMA_NAME = os.getenv('SCHEMA_NAME')


class BitrixSecrets:
    """     MSK_TOKEN = os.getenv('MSK_TOKEN')
        VLK_TOKEN = os.getenv('VLK_TOKEN')
        NKR_TOKEN = os.getenv('NKR_TOKEN')
        BTV_TOKEN = os.getenv('BTV_TOKEN') """
    def __init__(self):
        self.departments = {
            1: 'empty',
            2: os.getenv('MSK_TOKEN'),
            3: os.getenv('VLK_TOKEN'),
            4: os.getenv('NKR_TOKEN'),
            5: os.getenv('BTV_TOKEN')
        }

    async def token(self, department_id):
        return self.departments[department_id]
