import logging
from os import getenv


__initialized = False


def get_logger(name=''):
    global __initialized
    if not __initialized:
        logging.basicConfig(
            format='%(asctime)s | %(processName)-20s | %(name)-30s | %(levelname)-8s | %(message)s',
            level=getenv('LOG_LEVEL', 'INFO')
        )
        logging.captureWarnings(True)
        __initialized = True

    return logging.getLogger(name)
