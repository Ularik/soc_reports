DEV = False

DEBUG = True

SECRET_KEY = 'django-insecure-^fwo0knx+#^$%n^%^9h3l*dv_np^3t$2i2!ekwl9)ife8b-!a@'

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://192.168.100.104:8080', 'http://192.168.51.202:8080', 'http://192.168.100.109:8080']


DB_NAME_DEV = 'reports'
DB_USER_DEV = 'ular'
DB_PASS_DEV = 'admin'
DB_HOST_DEV = 'localhost'
DB_NAME_DEV_TEST = ''
DB_PORT_DEV = '5432'

DB_ENGINE =  'django.db.backends.oracle'
DB_NAME = 'reports'
DB_USER = 'ular'
DB_PASS = 'admin'
DB_HOST = 'localhost'
DB_NAME_TEST = ''
DB_PORT = '5432'

# Чат бот отправки логов
SEND_BOT = False
CHAT_ID = ''
BOT_ID = ''