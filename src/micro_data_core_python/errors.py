import logging
logger = logging.getLogger('primary')


class BaseError(Exception):
    pass


class AncileException(BaseError):
    def __init__(self, message):
        self.message = message
        logger.error(message)

    def __str__(self):
        return f'AncileException: {self.message}'


class ParseError(BaseError):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'ParseError: {self.message}'


class ConfigError(BaseError):
    def __init__(self, param, r_value, acceptable_vals):
        self.param = param
        self.r_value = r_value
        self.acceptable_vals = acceptable_vals

    def __str__(self) -> str:
        return (f'ConfigError: parameter {self.param} received invalid input '
                f'\'{self.r_value}\'. Valid parameters are {self.acceptable_vals}')