"""
Django settings for ASBJJ project.

Configurações otimizadas para produção e desenvolvimento.
"""

import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializar django-environ
env = environ.Env(
    DEBUG=(bool, False)
)

# Ler arquivo .env se existir
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-ep24b3!wp^l@rdar&ki!2bvgn)p09%22_90@584f=%9ph$1^3!')

# Security: Generate new secret key if using default
if SECRET_KEY == 'django-insecure-ep24b3!wp^l@rdar&ki!2bvgn)p09%22_90@584f=%9ph$1^3!':
    import warnings
    warnings.warn("Using default SECRET_KEY. Generate a new one for production!")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'asbjj.com.br', 'www.asbjj.com.br'])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
]

LOCAL_APPS = [
    'core',
    'accounts',
    'students',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'core.middleware.PerformanceMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Rate limiting apenas em produção
if not DEBUG:
    MIDDLEWARE.extend([
        'core.middleware.RateLimitMiddleware',
        'core.middleware.ErrorHandlingMiddleware',
    ])

ROOT_URLCONF = 'projeto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'projeto.wsgi.application'

# Database
DATABASES = {
    'default': env.db(default='sqlite:///db.sqlite3')
}

# Password validation
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
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações de autenticação
LOGIN_URL = '/admin/login/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

# Configurações de email
if env.bool('EMAIL_CONSOLE', default=False) or DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@asbjj.com.br')

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Django Authentication
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Django Allauth (desabilitado temporariamente)
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_USERNAME_REQUIRED = False
# ACCOUNT_AUTHENTICATION_METHOD = 'email'
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

# Configuração de login personalizado
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'

# Configurações de segurança
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
    SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
    CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)
    SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
    SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=True)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
    SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = 'require-corp'
    # Additional security headers
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Strict'
    # Password validation
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {
                'min_length': 12,
            }
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    X_FRAME_OPTIONS = 'SAMEORIGIN'

    # Forçar novo cookie de CSRF em dev (evita cookie antigo com flag Secure)
    CSRF_COOKIE_NAME = 'csrftoken_dev'
    CSRF_COOKIE_HTTPONLY = False

CSRF_TRUSTED_ORIGINS = [
    'https://asbjj.com.br',
    'https://www.asbjj.com.br'
]

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Session security
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True

# CSRF settings
CSRF_COOKIE_AGE = 3600
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'

# File upload security
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Admin security
ADMIN_URL = env('ADMIN_URL', default='admin/')

# WhatsApp configuration
ADMIN_WHATSAPP = env('ADMIN_WHATSAPP', default='')  # Formato: 5521999999999 (código país + DDD + número)

# Database optimization
DATABASES['default']['CONN_MAX_AGE'] = 60

# MySQL specific options
if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
    DATABASES['default']['OPTIONS'] = {
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        'charset': 'utf8mb4',
    }

# Static files optimization
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files optimization
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Template optimization
if not DEBUG:
    # Quando usar loaders customizados, APP_DIRS deve ser False
    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# Logging optimization
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Em desenvolvimento, confiar também em origens locais
if DEBUG:
    CSRF_TRUSTED_ORIGINS += [
        'http://127.0.0.1',
        'http://localhost',
        'http://127.0.0.1:8000',
        'http://localhost:8000',
    ]

# Quando atrás de proxy (ex.: Nginx), respeitar cabeçalho X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Configurações de cache
REDIS_URL = env('REDIS_URL', default='')
if REDIS_URL and not DEBUG:
    # Usar Redis apenas em produção quando disponível
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            },
            'KEY_PREFIX': env('CACHE_KEY_PREFIX', default='asbjj'),
            'TIMEOUT': 300,  # 5 minutes default
            'VERSION': 1,
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    # Usar cache local e sessões em banco para desenvolvimento
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Configurações do Celery (desabilitado temporariamente)
# CELERY_BROKER_URL = env('REDIS_URL', default='redis://127.0.0.1:6379/0')
# CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://127.0.0.1:6379/0')
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = TIME_ZONE

# Celery Beat Schedule
# from .celerybeat_schedule import CELERY_BEAT_SCHEDULE

# Configurações de logging
LOG_LEVEL = env('LOG_LEVEL', default='INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': LOG_LEVEL,
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'logs' / 'django.log'),
            'formatter': 'verbose',
            'level': LOG_LEVEL,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': LOG_LEVEL,
    },
}

# Configurações do Sentry (apenas em produção)
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN and not DEBUG:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    
    sentry_logging = LoggingIntegration(
        level=LOG_LEVEL,        # Capture info and above as breadcrumbs
        event_level=40,          # Send errors and above as events
    )
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
                cache_spans=True,
            ),
            sentry_logging,
        ],
        traces_sample_rate=env.float('SENTRY_TRACES_SAMPLE_RATE', default=0.1),
        send_default_pii=True,
        environment=env('SENTRY_ENVIRONMENT', default='production'),
    )

# Debug Toolbar (apenas em desenvolvimento)
if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]

# Configurações personalizadas do site
SITE_NAME = env('SITE_NAME', default='ASBJJ - Alexandre Salgado Brazilian Jiu-Jitsu')
SITE_URL = env('SITE_URL', default='https://asbjj.com.br')
ADMIN_EMAIL = env('ADMIN_EMAIL', default='admin@asbjj.com.br')
GOOGLE_ANALYTICS_ID = env('GOOGLE_ANALYTICS_ID', default='')
WHATSAPP_NUMBER = env('WHATSAPP_NUMBER', default='+5511999999999')