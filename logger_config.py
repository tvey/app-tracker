import sys

from loguru import logger


def setup_logger():
    fmt = '{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}'
    logger.add(sys.stdout, level='DEBUG', format=fmt)


setup_logger()
