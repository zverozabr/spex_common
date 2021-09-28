import logging
import logging.config
from os import getenv


__initialized = False


def get_logger(name=''):
    global __initialized
    if not __initialized:
        config = {
            'version': 1,
            'formatters': {
                'detailed': {
                    'class': 'logging.Formatter',
                    'format': '%(asctime)s | %(processName)-10s | %(name)-15s | %(levelname)-8s | %(message)s'
                },
                'simple': {
                    'class': 'logging.Formatter',
                    'format': '%(processName)-10s | %(name)-15s | %(levelname)-8s | %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                    'level': getenv('LOG_LEVEL', 'INFO')
                },
            }
        }
        logging.config.dictConfig(config)
        __initialized = True

    logging.getLogger(name)
