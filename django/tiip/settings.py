import os
import datetime
import sys
from distutils.util import strtobool
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'qu1nafi=f@#w8fz&)(i4h*-1@!gm4)dg^^@vt7!fhwjo!6qh9z')

DEBUG = bool(strtobool(os.environ.get('DEBUG', 'False')))

ALLOWED_HOSTS = ['.localhost', '.dev.whomaps.pulilab.com', '*']


# Application definition

INSTALLED_APPS = [
    'modeltranslation',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'azure',
    'rest_auth',
    'rest_auth.registration',
    'rest_framework',
    'rest_framework.authtoken',
    'django_extensions',
    'raven.contrib.django.raven_compat',
    'ordered_model',
    'rosetta',
    'corsheaders',
    'djcelery_email',
    'simple_history',
    'user',
    'core',
    'project',
    'toolkit',
    'country',
    'search',
    'scheduler',
    'cms',
    'simple-feedback',
]

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.ExceptionLoggingMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'tiip.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'core.context_processors.from_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'tiip.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': os.environ.get("DATABASE_URL", 'postgres'),
        'PORT': 5432,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGES = (
    ('en', _('English')),
    ('fr', _('French')),
    ('es', _('Spanish')),
    ('pt', _('Portuguese')),
    ('ar', _('Arabic')),
)
LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/usr/share/django/static'

MEDIA_ROOT = '/usr/share/django/media'
# MEDIA_ROOT = '/usr/share/nginx/html/media'
MEDIA_URL = '/media/'

FILE_UPLOAD_PERMISSIONS = 0o644

SITE_ID = int(os.environ.get('SITE_ID', 1))
CI_RUN = bool(os.environ.get('CI_RUN', False))

CORS_ORIGIN_ALLOW_ALL = True

# Rest framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user_profile_id': user.userprofile.id if user.userprofile else None,
        'account_type': user.userprofile.account_type if user.userprofile else None,
        'is_superuser': user.is_superuser
    }


JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER': jwt_response_payload_handler,
    'JWT_AUTH_HEADER_PREFIX': 'Token',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7)
}

# django-allauth and rest-auth settings
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    # 'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods
    'allauth.account.auth_backends.AuthenticationBackend',
)

REST_USE_JWT = True
REST_AUTH_SERIALIZERS = {
    'JWT_SERIALIZER': 'user.serializers.ProfileJWTSerializer',
    # 'PASSWORD_RESET_SERIALIZER': 'user.serializers.PasswordResetHTMLEmailSerializer'
}

SOCIALACCOUNT_PROVIDERS = {
    'azure': {
        'APP': {
            'client_id': os.environ.get('AZURE_CLIENT_ID', ''),
            'secret': os.environ.get('AZURE_SECRET', ''),
        },
    }
}
SOCIALACCOUNT_ADAPTER = 'user.adapters.MyAzureAccountAdapter'
SOCIALACCOUNT_AZURE_TENANT = os.environ.get('AZURE_TENANT', '')
SOCIALACCOUNT_CALLBACK_URL = os.environ.get('AZURE_CALLBACK_URL', 'http://localhost/accounts/azure/login/callback/')
LOGIN_REDIRECT_URL = '/'

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_ADAPTER = 'user.adapters.DefaultAccountAdapterCustom'
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
ACCOUNT_EMAIL_CONFIRMATION_HMAC = False  # This is for backwards compat, should move to True to not store it in DB
DEFAULT_FROM_EMAIL = "UNICEF T4D & Innovation Inventory Portal <noreply@tiip.unitst.org>"

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_SENDING_PRODUCTION = os.environ.get('EMAIL_SENDING_PRODUCTION', False)

REDIS_URL = os.environ.get('REDIS_URL', 'redis')

# Celery settings
BROKER_URL = 'redis://{}:6379/0'.format(REDIS_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

ODK_SYNC_PERIOD = 1  # hours
ODK_CREDENTIALS = {
    'username': 'f1987_final@pulilab.com',
    'password': 'secret'
}
ODK_SERVER_PROTOCOL = "https"
ODK_SERVER_HOST = "odk.digitalhealthatlas.org"
ODK_SERVER_USER = "odk"
ODK_TABLE_NAME = 'dha_form'
ODK_SYNC_ENABLED = bool(os.environ.get('ODK_SYNC_ENABLED', False))


# PRODUCTION SETTINGS
if SITE_ID in [3, 4]:
    if SITE_ID == 3:  # QA
        # Mailgun settings
        EMAIL_USE_TLS = True
        EMAIL_HOST = "smtp.mailgun.org"
        EMAIL_HOST_USER = "postmaster@whomaps.pulilab.com"
        EMAIL_HOST_PASSWORD = "5ede15430fbf90989648a0fe12e379cc"
        EMAIL_PORT = 587
        EMAIL_BACKEND = 'core.middleware.TestCeleryEmailBackend'
        TEST_FORCED_TO_ADDRESS = ["t@pulilab.com", "f@pulilab.com"]

        RAVEN_CONFIG = {
            'dsn': 'https://0b6cb1cc48594b499991547adb024864:f851242c5437437ca866e749c965d8ec@sentry.vidzor.com/29',
        }
    elif SITE_ID == 4:  # PROD AZURE
        EMAIL_HOST = "extmail01.unicef.org"
        EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

        RAVEN_CONFIG = {
            'dsn': 'https://bca06cdc7c9545faac1db722363bc313:5e185d21565d453e83667556ad385f92@sentry.vidzor.com/31',
        }

    CELERYBEAT_SCHEDULE = {
        "send_project_approval_digest": {
            "task": 'send_project_approval_digest',
            "schedule": datetime.timedelta(days=1),
        },
        "project_still_in_draft_notification": {
            "task": 'project_still_in_draft_notification',
            "schedule": datetime.timedelta(days=31),
        },
        "published_projects_updated_long_ago": {
            "task": 'published_projects_updated_long_ago',
            "schedule": datetime.timedelta(days=31),
        },
    }
    if ODK_SYNC_ENABLED:
        CELERYBEAT_SCHEDULE.update(
            {
                "sync_project_from_odk": {
                    "task": 'sync_project_from_odk',
                    "schedule": datetime.timedelta(hours=ODK_SYNC_PERIOD)
                }
            })

    DEBUG = False

    ALLOWED_HOSTS = ['uni-tiip-dev', '40.113.114.39', 'tiip.unitst.org', '.tipp.pulilab.com', 'nginx:9010', 'nginx']

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        ),
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
        )
    }

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://{}:6379/1".format(REDIS_URL),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

FROM_EMAIL = DEFAULT_FROM_EMAIL


# Geodata settings
GEOJSON_TEMP_DIR = os.path.join(os.path.dirname(__file__), os.pardir, 'temp/')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/tmp/whomaps.log',
            'maxBytes': 10000000,
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/login/'

ROSETTA_STORAGE_CLASS = 'rosetta.storage.CacheRosettaStorage'
ROSETTA_WSGI_AUTO_RELOAD = True
ROSETTA_MESSAGES_PER_PAGE = 25

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'translations'),  # don't move this, update_translations mgmt cmd is using it
    os.path.join(BASE_DIR, 'locale'),
    os.path.join(BASE_DIR, 'cms/locale'),
    os.path.join(BASE_DIR, 'core/locale'),
    os.path.join(BASE_DIR, 'country/locale'),
    os.path.join(BASE_DIR, 'project/locale'),
    os.path.join(BASE_DIR, 'search/locale'),
    os.path.join(BASE_DIR, 'toolkit/locale'),
    os.path.join(BASE_DIR, 'user/locale'),
]

for arg in sys.argv:
    if 'test' in arg:
        DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'

if SITE_ID == 4:
    ENVIRONMENT_NAME = "PRODUCTION"
    ENVIRONMENT_COLOR = "red"
elif SITE_ID == 3:
    ENVIRONMENT_NAME = "QA / STAGING"
    ENVIRONMENT_COLOR = "orange"
else:
    ENVIRONMENT_NAME = "DEVELOPMENT"
    ENVIRONMENT_COLOR = "blue"


if CI_RUN:
    STATIC_ROOT = "/home/circleci/tiip/nginx/site/static/"
    MEDIA_ROOT = "/home/circleci/tiip/django/media/"

OSM_MAP_CLI_KEY = 'a9ea45b5-ab37-4323-8263-767aa5896113'
CSRF_TRUSTED_ORIGINS = ['uni-tiip-dev', '40.113.114.39', 'tiip.unitst.org', 'tipp.pulilab.com']
