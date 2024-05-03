import os
import sys

import dotenv
from loguru import logger

dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_API_TOKEN')

DATABASE_URL = os.getenv('DATABASE_URL', '')
SQLALCHEMY_ECHO = bool(os.getenv('SQLALCHEMY_ECHO'))

logger.add(
    sys.stdout,
    level='DEBUG',
    format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
)
