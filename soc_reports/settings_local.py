DEV = False

DEBUG = True

SECRET_KEY = 'django-insecure-********'

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://site.local', 'http://localhost:5173/']


DB_NAME_DEV = ''
DB_USER_DEV = ''
DB_PASS_DEV = ''
DB_HOST_DEV = ''
DB_NAME_DEV_TEST = ''
DB_PORT_DEV = '5432'

DB_ENGINE =  'django.db.backends.oracle'
DB_NAME = ''
DB_USER = ''
DB_PASS = ''
DB_HOST = ''
DB_NAME_TEST = ''
DB_PORT = ''

# Чат бот отправки логов
SEND_BOT = False
CHAT_ID = ''
BOT_ID = ''