import yaml

with open('./config/config.yaml', 'r') as f:
    configs = yaml.safe_load(f)

with open('./config/oauth.yaml', 'r') as f:
    oauth = yaml.safe_load(f)

def _postgres_url(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST,
                  POSTGRES_PORT, POSTGRES_DB):
    return {"SQLALCHEMY_DATABASE_URI": f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'}

def configure_app(app):
    app.config.update(**configs['server'])
    app.config.update(_postgres_url(**configs['database']))
    app.config.update(**configs['security'])
    app.config.update(**configs['mail'])
    app.config.update(**oauth['secrets'])

REDIS_CONFIG = configs['redis']
ENABLE_CACHE = configs['operational']['CACHE']