POSTGRES_USER='postgres'
POSTGRES_PASSWORD='postgres'
POSTGRES_HOST='localhost'
POSTGRES_PORT=5432
POSTGRES_DB='ancile_dev_db'

DATABASE_CONNECTION_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

REDIS_CONFIG = {'host': 'localhost',
                'port': 6379,
                'db': 1}