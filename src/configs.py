import os
from src.micro_data_core_python.errors import ConfigError


def parse_env_bool(name: str, arg: str) -> bool:
    """Get T/F from env variable.

    :param str name: the environment variable name. Passed through for errors.
    :param str arg: the value to be converted to a boolean
    :return: True or False
    """
    arg = arg.lower().strip()
    if arg in {'false'}:
        return False
    elif arg in {'true'}:
        return True
    else:
        raise ConfigError(name, arg, ['true', 'false'])


enable_cache = parse_env_bool('CACHE', os.getenv('CACHE', 'false'))
enable_logs = parse_env_bool('LOGGING', os.getenv('LOGGING', 'true'))
