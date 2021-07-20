from os import path, environ
from dotenv import dotenv_values

trues = ['true', 'yes']
falses = ['false', 'no']
int_keys = ['MAX_CONTENT_LENGTH']


def load(mode='', update_environ=True):
    mode = environ.get('MODE', mode)

    file = f'.{mode}' if mode else ''

    file = path.join(
        path.dirname(__file__),
        f'.env{file}'
    )
    local = f'{file}.local'

    config = {
        **dotenv_values(local if path.exists(local) else file)
    }

    for key, value in config.items():
        if update_environ:
            environ[key] = value

        if value:
            if type(value) is str and value.lower() in trues:
                value = True
                config[key] = value
            elif type(value) is str and value.lower() in falses:
                value = False
                config[key] = value
            elif key.upper() in int_keys:
                value = int(value)
                config[key] = value

    return config
