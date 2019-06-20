import yaml

with open('./config/config.yaml', 'r') as f:
    configs = yaml.safe_load(f)

with open('./config/oauth.yaml', 'r') as f:
    oauth = yaml.safe_load(f)

REDIS_CONFIG = configs['redis']
ENABLE_CACHE = configs['operational']['CACHE']
ENABLE_LOGGING = configs['operational']['LOGGING']


def _postgres_url(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST,
                  POSTGRES_PORT, POSTGRES_DB):
    return {"SQLALCHEMY_DATABASE_URI": f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'}

def configure_app(app):
    app.config.update(**configs['server'])
    app.config.update(_postgres_url(**configs['database']))
    app.config.update(**configs['security'])
    app.config.update(**configs['mail'])
    app.config.update(**oauth['secrets'])

    if ENABLE_LOGGING:
        import os
        import logging
        import logging.handlers as handlers
        import sys

        if not os.path.isdir('logs'):
            os.mkdir('logs')

        root = logging.getLogger()

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        file_log = logging.FileHandler('logs/info.log')
        file_log.setLevel(logging.INFO)
        file_log.setFormatter(formatter)
        stream = logging.StreamHandler(stream=sys.stdout)
        stream.setLevel(logging.DEBUG)
        file_log.setFormatter(formatter)

        root.addHandler(file_log)
        root.addHandler(stream)

        flask_logger = logging.getLogger('werkzeug')
        flask_file = handlers.RotatingFileHandler('logs/access.log',
                                                maxBytes=2**22,
                                                backupCount=3)
        flask_file.setLevel(logging.DEBUG)

        flask_logger.addHandler(flask_file)
        flask_logger.propagate = False
