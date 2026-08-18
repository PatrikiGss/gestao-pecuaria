"""
Django settings para o projeto Gestao Pecuaria.

Gerado por 'django-admin startproject' com Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
import sys
from pathlib import Path
from decouple import config, Csv
from datetime import timedelta  

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

APPS_DIR = os.path.join(BASE_DIR, 'apps')
# Adiciona APPS_DIR no início da lista de caminhos do sistema
sys.path.insert(0, APPS_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = []

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_APPS = [ 
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

PROJECT_APPS = [
    'core.apps.CoreConfig',
    'autenticacao.apps.AutenticacaoConfig',
]

INSTALLED_APPS = PROJECT_APPS + THIRD_APPS + DJANGO_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',#postgresql  sqlite3
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# Adiciona o modelo customizado de usuário
AUTH_USER_MODEL = 'autenticacao.Usuario'

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
# Arquivos-fonte versionados no repositorio
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# Destino do 'collectstatic' (gerado, nao versionar)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS Headers Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:7777", 
    "http://127.0.0.1:7777",

]


CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:7777",
    "http://127.0.0.1:7777",
]

#DRF Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # AllowAny  IsAuthenticated
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # O tempo de vida do token de acesso
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # O tempo de vida do token de refresh
    'ROTATE_REFRESH_TOKENS': True,  # Gira os tokens de refresh automaticamente
    'BLACKLIST_AFTER_ROTATION': True,  # Coloca o token antigo na lista negra
    'ALGORITHM': 'HS256',  # Algoritmo de criptografia
    'SIGNING_KEY': SECRET_KEY,  # Usa a chave secreta definida anteriormente
    'AUTH_HEADER_TYPES': ('Bearer',),  # Tipo de cabeçalho de autenticação
    'TOKEN_USER_CLASS': 'autenticacao.Usuario',  # O modelo de usuário que será autenticado
    'TOKEN_BLACKLIST_ENABLED': True,  # Habilita o uso de blacklist para tokens
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),  # Para tokens deslizantes, caso use
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}