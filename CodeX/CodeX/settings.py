from pathlib import Path
import os
import dj_database_url

# BASE_DIR will be D:/CodeX/CodeX
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Render will set this via environment variable if generateValue: true is used in render.yaml
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-local-dev')

# SECURITY WARNING: don't run with debug turned on in production!
# Render will set DEBUG to 'False' or '0' via environment variable.
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS should include your Render service URL.
# The '.onrender.com' will cover your Render domain.
# Add 'localhost' and '127.0.0.1' for local development.
ALLOWED_HOSTS_STRING = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,.onrender.com')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STRING.split(',') if host.strip()]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # For serving static files with Whitenoise in dev
    'django.contrib.staticfiles',
    'core',
    # google authentication
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    # Our custom error handling middleware should be first to catch all exceptions
    'CodeX.middleware.ErrorHandlingMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware', # Django Allauth middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Site ID for allauth (required)
SITE_ID = 1

# Provider specific settings for django-allauth (Google OAuth)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            # These will be loaded from environment variables on Render
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET', ''),
            'key': ''  # Usually not needed for Google
        }
    }
}

# Allauth settings
SOCIALACCOUNT_LOGIN_ON_GET = True # Skip intermediate confirmation page
SOCIALACCOUNT_AUTO_SIGNUP = True # Automatically create users
ACCOUNT_EMAIL_VERIFICATION = "none" # Or "mandatory" / "optional" as per your needs
ACCOUNT_EMAIL_REQUIRED = True # Usually a good idea
ACCOUNT_AUTHENTICATION_METHOD = "username_email" # Allow login with username or email

LOGIN_REDIRECT_URL = '/core/dashboard/'
LOGIN_URL = '/accounts/login/' # Default allauth login URL
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/' # Redirect after logout

# Project's root URL configuration
# This should point to D:/CodeX/CodeX/CodeX/urls.py
ROOT_URLCONF = 'CodeX.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Corrected DIRS to point to D:/CodeX/CodeX/CodeX/templates/
        # BASE_DIR is D:/CodeX/CodeX, so 'CodeX/templates' is correct.
        'DIRS': [os.path.join(BASE_DIR, 'CodeX', 'templates')],
        'APP_DIRS': True, # Looks for templates within app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', # Required by allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI application path
# This should point to D:/CodeX/CodeX/CodeX/wsgi.py
WSGI_APPLICATION = 'CodeX.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# Render will provide DATABASE_URL environment variable.
# The default for local dev will be db.sqlite3 in the repository root (D:/CodeX/db.sqlite3).
# BASE_DIR is D:/CodeX/CodeX, so BASE_DIR.parent is D:/CodeX
# The build script runs from D:/CodeX, so migrations will apply to D:/CodeX/db.sqlite3
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR.parent / "db.sqlite3"}', # Fallback for local dev
        conn_max_age=600,
        conn_health_checks=True,
    )
}
# If DEBUG is False (on Render), and DATABASE_URL is not set for a managed DB,
# 'sqlite:///db.sqlite3' in render.yaml would create an ephemeral DB in the service's runtime environment.
# The path above ensures that local dev uses the repo root db.sqlite3.
# For Render, if you're using its ephemeral SQLite, the one from build (in repo root) is copied.
# For a persistent Render SQLite disk, you'd set DATABASE_URL to e.g., 'sqlite:////var/data/db.sqlite3'
# and mount the disk at /var/data.


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/' # URL prefix for static files served by the web server

# Directories where Django will look for static files during development
# and for collectstatic.
# BASE_DIR is D:/CodeX/CodeX, so 'CodeX/static' is correct for D:/CodeX/CodeX/CodeX/static/
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'CodeX', 'static'),
]

# Directory where collectstatic will gather all static files for production.
# This should be a top-level directory in your service on Render.
# BASE_DIR is D:/CodeX/CodeX.
# BASE_DIR.parent is D:/CodeX.
# So, this will be D:/CodeX/staticfiles_build/static (or similar on Render's filesystem)
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'staticfiles_build', 'static')


# Whitenoise storage for compressed static files and cache-busting.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings for production (Render)
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True # Ensure all non-HTTPS requests are redirected to HTTPS
    SECURE_HSTS_SECONDS = 31536000 # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # For Render's proxy