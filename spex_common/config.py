from os import path, environ, getcwd
from dotenv import dotenv_values
from .modules.logging import get_logger

trues = ['true', 'yes']
falses = ['false', 'no']
int_keys = ['MAX_CONTENT_LENGTH']


def _convert_value(key, value):
    if value:
        if key.upper() in int_keys:
            return int(value)

        if type(value) is str and value.lower() in trues:
            return True

        if type(value) is str and value.lower() in falses:
            return False

    return value


def _get_config(working_dir, mode=None):
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
    ignore_env_files = environ.get('CONFIG_IGNORE_ENV_FILES', 'False')

    from_env_files = {} if ignore_env_files else {
        **_get_config(working_dir),
        **_get_config(working_dir, mode),
    }

    config = {
        **environ.copy(),
        **from_env_files,
    }

    for key, value in config.items():
        if value is None and environ[key] is not None:
            config[key] = environ[key]

        if update_environ:
            environ[key] = value if value is not None else environ[key]

        config[key] = _convert_value(key, value)

    get_logger('spex.common.config').info(f'uses MODE={mode}')

    return config
