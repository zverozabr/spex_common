import logging
from os import getenv


__initialized = False


def get_logger(name=''):
    global __initialized
    if not __initialized:
        logging.basicConfig(
            format='%(asctime)s | %(processName)-20s | %(name)-30s | %(levelname)-8s | %(message)s',
            level=getenv('SPEX_LOG_LEVEL', 'DEBUG')
        )
        logging.captureWarnings(True)
        level = logging.getLevelName(logging.getLogger().level)
        logging.getLogger('spex.common.logging').info(f'LOG_LEVEL={level}')
        __initialized = True

    return logging.getLogger(name)
