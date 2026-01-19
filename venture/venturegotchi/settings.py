"""
Django settings for venturegotchi project.
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis do .env local (não obrigatório no Render)
load_dotenv(BASE_DIR / ".env")

# =====================================
# CONFIGURAÇÕES DE SEGURANÇA
# =====================================

SECRET_KEY = os.getenv("SECRET_KEY", "chave-insegura-fallback")

DEBUG = os.getenv("DEBUG", "False") == "True"

# ALLOWED_HOSTS configurado para Render
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_host:
    ALLOWED_HOSTS.append(render_host)


# =====================================
# APLICAÇÕES INSTALADAS
# =====================================

INSTALLED_APPS = [
    'accounts',
    'core',
    'dashboard',
    'missions',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

AUTH_USER_MODEL = "accounts.User"  # Seu modelo customizado


# =====================================
# MIDDLEWARE
# =====================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # Serve arquivos estáticos no Render (antes do SessionMiddleware)
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'venturegotchi.urls'


# =====================================
# TEMPLATES
# =====================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Pode adicionar templates globais aqui se quiser
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'venturegotchi.wsgi.application'


# =====================================
# BANCO DE DADOS — CONFIGURADO PARA RENDER
# =====================================

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}


# =====================================
# VALIDADORES DE SENHA
# =====================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =====================================
# LOCALIZAÇÃO
# =====================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_TZ = True


# =====================================
# ARQUIVOS ESTÁTICOS E MÍDIAS
# =====================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise — compressão otimizada
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Arquivos enviados pelo usuário (se for ter uploads futuramente)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =====================================
# DEFAULT PK
# =====================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
