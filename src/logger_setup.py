import logging

import os

if not os.path.isdir('logs'):
    os.mkdir('logs')

primary = logging.getLogger('primary')
primary.setLevel(logging.DEBUG)
api_logger = logging.getLogger('api')
api_logger.setLevel(logging.INFO)

debug_file = logging.FileHandler('logs/debug.log')
api_file = logging.FileHandler('logs/api_calls.log')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
debug_file.setFormatter(formatter)
api_file.setFormatter(formatter)

primary.addHandler(debug_file)
api_logger.addHandler(debug_file)
api_logger.addHandler(api_file)