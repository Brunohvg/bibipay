from pathlib import Path
from decouple import config
from django.contrib.messages import constants as messages

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = config('SECRET_KEY', default='unsafe-secret-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',') if config('ALLOWED_HOSTS', default='') else []

# Apps
INSTALLED_APPS = [
    # Third-party apps
    'widget_tweaks',

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'apps.core',
    'apps.accounts',
    'apps.dashboard',
    'apps.sales',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Templates
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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database (SQLite para dev, simples para produção)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3' if DEBUG else config('DATABASE_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': BASE_DIR / 'db.sqlite3' if DEBUG else config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': None if DEBUG else config('DB_USER', default=''),
        'PASSWORD': None if DEBUG else config('DB_PASSWORD', default=''),
        'HOST': None if DEBUG else config('DB_HOST', default=''),
        'PORT': None if DEBUG else config('DB_PORT', default=''),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static & Media
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Logging simples
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'DEBUG' if DEBUG else 'INFO'},
}

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model

LOGIN_REDIRECT_URL = '/TESTE'  # redireciona após login bem-sucedido
LOGOUT_REDIRECT_URL = '/accounts/login/'  # redireciona após logout
AUTH_USER_MODEL = 'accounts.User' # Modelo de usuário customizado


AUTHENTICATION_BACKENDS = [
    'apps.core.auth.backends.CPFOrEmailBackend',  # nosso backend custom
    'django.contrib.auth.backends.ModelBackend', # padrão
]