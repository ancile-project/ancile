import logging
logger = logging.getLogger('primary')

class AncileException(Exception):
    def __init__(self, message):
        logger.error(message)