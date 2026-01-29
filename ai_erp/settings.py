"""
Django-Einstellungen für das ai_erp Projekt.

Generiert durch 'django-admin startproject' mit Django 5.2.10.

Für mehr Informationen zu dieser Datei, siehe
https://docs.djangoproject.com/en/5.2/topics/settings/

Für die vollständige Liste der Einstellungen und ihrer Werte, siehe
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path

# Pfade innerhalb des Projekts bauen wie folgt: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start Entwicklungseinstellungen - ungeeignet für Produktion
# Siehe https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SICHERHEITSWARNUNG: Den Secret Key in Produktion geheim halten!
SECRET_KEY = 'django-insecure-2q(21#^^2x$v$yr8unlv@0-mhii*fno0r2+9^v@y@0%y2i^9#q'

# SICHERHEITSWARNUNG: Debug-Modus in Produktion ausschalten!
DEBUG = True

ALLOWED_HOSTS = []


# App-Definition

INSTALLED_APPS = [
    # Django Core Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party Apps
    'django_fsm',
    
    # Core App (Fundament - Keine Business-Logik)
    'core',
    
    # Business Apps (Modular)
    'apps.users',
    'apps.ai_engine',
    'apps.sales',
    'apps.inventory',
    'apps.finance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ai_erp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'ai_erp.wsgi.application'


# Datenbank
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Datenbank
# PostgreSQL Konfiguration (Produktion)
# Vorerst SQLite für initiales Setup - vor Deployment auf PostgreSQL wechseln
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    # Produktions-PostgreSQL-Konfiguration (einkommentieren wenn bereit):
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': os.getenv('DB_NAME', 'ai_erp'),
    #     'USER': os.getenv('DB_USER', 'postgres'),
    #     'PASSWORD': os.getenv('DB_PASSWORD'),
    #     'HOST': os.getenv('DB_HOST', 'localhost'),
    #     'PORT': os.getenv('DB_PORT', '5432'),
    # }
}


# Passwort-Validierung
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalisierung
# https://docs.djangoproject.com/en/5.2/topics/i18n/

# Lokalisierung für den deutschen Markt
LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_TZ = True


# Statische Dateien (CSS, JavaScript, Bilder)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Für Produktion collectstatic

# Mediendateien (Benutzer-Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Custom User Model (KRITISCH: Muss vor der ersten Migration gesetzt werden)
AUTH_USER_MODEL = 'users.User'

# Standard Primary Key Feldtyp
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
