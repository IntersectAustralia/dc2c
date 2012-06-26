from settings import *

DEBUG = False

DATABASES = {
    'default': {
        # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tardis_db',
        'USER': 'tardis',
        'PASSWORD': 'tardis',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

SYSTEM_LOG_FILENAME = '/var/mytardis/log/request.log'
MODULE_LOG_FILENAME = '/var/mytardis/log/tardis.log'

FILE_STORE_PATH = '/var/mytardis/store'
STAGING_PATH = '/var/mytardis/staging'

SINGLE_SEARCH_ENABLED=True

OAI_DOCS_PATH = '/var/mytardis/oai'

MIDDLEWARE_CLASSES = (
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'tardis.tardis_portal.minidetector.Middleware',
    'tardis.tardis_portal.logging_middleware.LoggingMiddleware',
    'tardis.tardis_portal.auth.AuthorizationMiddleware',
#    'ajaxerrors.middleware.ShowAJAXErrors',
    'django.middleware.transaction.TransactionMiddleware')

