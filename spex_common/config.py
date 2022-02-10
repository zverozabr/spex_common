from os import path, environ, getcwd
from dotenv import dotenv_values
from .modules.logging import get_logger

trues = ['true', 'yes']
falses = ['false', 'no']
int_keys = ['MAX_CONTENT_LENGTH']


def _get_config(mode, working_dir):
    main = f'.{mode}' if mode else ''

    main = path.join(
        working_dir if working_dir is not None else path.dirname(__file__),
        f'.env{main}'
    )
    local = f'{main}.local'

    config = {}

    if path.exists(main):
        config = {**dotenv_values(main)}

    if path.exists(local):
        config = {
            **config,
            **dotenv_values(local)
        }

    return config


def load_config(mode='', update_environ=True, working_dir=getcwd()):
    mode = environ.get('MODE', mode)

    config = {
        **environ.copy(),
        **_get_config('', working_dir),
        **_get_config(mode, working_dir),
    }

    for key, value in config.items():
        if value is None and environ[key] is not None:
            config[key] = environ[key]

        if update_environ:
            environ[key] = value if value is not None else environ[key]

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

    get_logger('spex.common.config').info(f'uses MODE={mode}')

    return config
