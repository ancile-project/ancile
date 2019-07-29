import yaml

with open("./config/config.yaml", "r") as f:
    configs = yaml.safe_load(f)

REDIS_CONFIG = configs["redis"]
DATABASE_CONFIG = configs["database"]
ENABLE_CACHE = configs["CACHE"]
ENABLE_LOGGING = configs["LOGGING"]
SECRET_KEY = configs["SECRET_KEY"]
SERVER_NAME = configs["SERVER_NAME"]

LANGUAGE_CODE = configs["LANGUAGE_CODE"]
TIME_ZONE = configs["TIME_ZONE"]
SERVER_DEBUG = configs["SERVER_DEBUG"]
