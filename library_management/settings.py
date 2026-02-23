"""
Django settings for library_management project.
"""

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================
# SECURITY
# ==============================================================
SECRET_KEY = config('SECRET_KEY', default='django-insecure-ne2gr5rjaq$#t)s@ge-z!yg9*^s)6o=+njo77weph^hj1f389(')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']


# ==============================================================
# APPLICATIONS
# ==============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reports',
    'reservation',
    'activitylog',
    'reviews',

    # Third-party
    'crispy_forms',
    'crispy_bootstrap5',

    # Your Apps
    'accounts',
    'books',
    'circulation',
    'dashboard',
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

ROOT_URLCONF = 'library_management.urls'


# ==============================================================
# TEMPLATES
# ==============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # ← Global templates folder
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

WSGI_APPLICATION = 'library_management.wsgi.application'


# ==============================================================
# DATABASE (MySQL)
# ==============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='library_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
    }
}


# ==============================================================
# CUSTOM USER MODEL
# ==============================================================
AUTH_USER_MODEL = 'accounts.User'


# ==============================================================
# PASSWORD VALIDATION
# ==============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==============================================================
# INTERNATIONALIZATION
# ==============================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'   # ← Changed to India timezone
USE_I18N = True
USE_TZ = True


# ==============================================================
# STATIC & MEDIA FILES
# ==============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ==============================================================
# LOGIN / LOGOUT REDIRECTS
# ==============================================================
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'


# ==============================================================
# CRISPY FORMS (Bootstrap 5)
# ==============================================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# ==============================================================
# DEFAULT PRIMARY KEY
# ==============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'