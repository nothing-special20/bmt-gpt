"""
Django settings for bmt-gpt-saas project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import environ
from datetime import timedelta
from pathlib import Path

from django.utils.translation import gettext_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR,  ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='SZgSLJMuMqtwQLbgidgkKdtOeboEdPfVMIxxzzWC')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

ALLOWED_HOSTS = [
    'jungleinsightz.com',
    'www.jungleinsightz.com',
    'localhost',
]

# Your email config goes here.
# see https://github.com/anymail/django-anymail for more details / examples
# To use mailgun, comment out the lines below and make sure your key and domain
# are available in the environment.
# EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'

ANYMAIL = {
    "MAILGUN_API_KEY": env('MAILGUN_API_KEY', default=None),
    "MAILGUN_SENDER_DOMAIN": env('MAILGUN_SENDER_DOMAIN', default=None),
}

SERVER_EMAIL = env('CONTACT_EMAIL', default=None)
DEFAULT_FROM_EMAIL = env('CONTACT_EMAIL', default=None)
ADMINS = [('Your Name', env('CONTACT_EMAIL', default=None)),]


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.forms',
    'channels',
]

# Put your third-party apps here
THIRD_PARTY_APPS = [
    'allauth',  # allauth account/registration management
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'allauth_2fa',
    'rest_framework',
    'drf_spectacular',
    'celery_progress',
    'hijack',  # "login as" functionality
    'hijack.contrib.admin',  # hijack buttons in the admin
    'djstripe',  # stripe integration
    'waffle',
]

PEGASUS_APPS = [
    'pegasus.apps.examples.apps.PegasusExamplesConfig',
    'pegasus.apps.employees.apps.PegasusEmployeesConfig',
]

# Put your project-specific apps here
PROJECT_APPS = [
    'apps.subscriptions.apps.SubscriptionConfig',
    'apps.users.apps.UserConfig',
    'apps.web',
    'apps.teams.apps.TeamConfig',
    'apps.teams_example.apps.TeamsExampleConfig',
    'apps.docchatgpt.apps.DocChatGptConfig',
    'apps.amazon.apps.AmazonConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PEGASUS_APPS + PROJECT_APPS

ASGI_APPLICATION = 'bmt_gpt.asgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'apps.teams.middleware.TeamsMiddleware',
    'apps.web.locale_middleware.UserLocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'hijack.middleware.HijackUserMiddleware',
    'waffle.middleware.WaffleMiddleware',
]

ROOT_URLCONF = 'bmt_gpt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.web.context_processors.project_meta',
                'apps.teams.context_processors.team',
                 # this line can be removed if not using google analytics
                'apps.web.context_processors.google_analytics_id',
                'apps.web.context_processors.microsoft_clarity_id',
                'apps.web.context_processors.crisp_chat_id',
            ],
        },
    },
]

WSGI_APPLICATION = 'bmt_gpt.wsgi.application'

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if 'DATABASE_URL' in env:
    DATABASES = {
        'default': env.db()
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env('DJANGO_DATABASE_NAME', default='bmt_gpt'),
            'USER': env('DJANGO_DATABASE_USER', default='postgres'),
            'PASSWORD': env('DJANGO_DATABASE_PASSWORD', default='***'),
            'HOST': env('DJANGO_DATABASE_HOST', default='db'),
            'PORT': env('DJANGO_DATABASE_PORT', default='5432'),
        }
    }

# Auth / login stuff

# Django recommends overriding the user model even if you don't think you need to because it makes
# future changes much easier.
AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = '/'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Allauth setup

ACCOUNT_ADAPTER = 'apps.teams.adapter.AcceptInvitationAdapter'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

ACCOUNT_FORMS = {
    'signup': 'apps.teams.forms.TeamSignupForm',
}


# User signup configuration: change to "mandatory" to require users to confirm email before signing in.
# or "optional" to send confirmation emails but not require them
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

ALLAUTH_2FA_ALWAYS_REVEAL_BACKUP_TOKENS = False

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)


# enable social login
SOCIALACCOUNT_PROVIDERS = { 
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }, 
    'twitter': {},
}


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
LANGUAGE_COOKIE_NAME = 'bmt_gpt_language'
LANGUAGES = [
    ('en', gettext_lazy('English')),
    ('fr', gettext_lazy('French')),
]
LOCALE_PATHS = (
    BASE_DIR / 'locale',
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = BASE_DIR / 'static_root'
STATIC_URL = '/staticfiles/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
    '/staticfiles/'
]

# uncomment to use manifest storage to bust cache when file change
# note: this may break some image references in sass files which is why it is not enabled by default
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

# future versions of Django will use BigAutoField as the default, but it can result in unwanted library
# migration files being generated, so we stick with AutoField for now.
# change this to BigAutoField if you're sure you want to use it and aren't worried about migrations.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Email setup

# use in development
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# use in production
# see https://github.com/anymail/django-anymail for more details/examples
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'

# Django sites

SITE_ID = 1

# DRF config
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Jungle Insightz',
    'DESCRIPTION': 'Use GPT to analyze your reviews to improve your Amazon Listing',
    'VERSION': '0.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
    "SWAGGER_UI_SETTINGS": {
        "displayOperationId": True,
    },
}

# Celery setup (using redis)
if 'REDIS_URL' in env:
    REDIS_URL = env('REDIS_URL')
elif 'REDIS_TLS_URL' in env:
    REDIS_URL = env('REDIS_TLS_URL')
else:
    REDIS_HOST = env('REDIS_HOST', default='localhost')
    REDIS_PORT = env('REDIS_PORT', default='6379')
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

if REDIS_URL.startswith('rediss'):
    REDIS_URL = f"{REDIS_URL}?ssl_cert_reqs=none"

# CELERY_BROKER_URL = CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

# Waffle config

WAFFLE_FLAG_MODEL = 'teams.Flag'

# Pegasus config

# replace any values below with specifics for your project
PROJECT_METADATA = {
    'NAME': "Jungle Insightz - GPT for Amazon Sellers",
    'URL': 'http://www.jungleinsightz.com',
    'DESCRIPTION': gettext_lazy('Use GPT to analyze your reviews to improve your Amazon Listing'),
    'IMAGE': 'https://upload.wikimedia.org/wikipedia/commons/2/20/PEO-pegasus_black.svg',
    'KEYWORDS': 'SaaS, django',
    'CONTACT_EMAIL': env('CONTACT_EMAIL', default=''),
    'LOOM_DEMO_URL': env('LOOM_DEMO_URL', default=''),
}

USE_HTTPS_IN_ABSOLUTE_URLS = False  # set this to True in production to have URLs generated with https instead of http

ADMINS = [('bmt', env('CONTACT_EMAIL', default=None))]

# Add your google analytics ID to the environment or default value to connect to Google Analytics
GOOGLE_ANALYTICS_ID = env('GOOGLE_ANALYTICS_ID', default='')

MICROSOFT_CLARITY = env('MICROSOFT_CLARITY', default='')

CRISP_ID = os.environ.get('CRISP_ID', '')

# Stripe config

# modeled to be the same as https://github.com/dj-stripe/dj-stripe
STRIPE_LIVE_PUBLIC_KEY = env("STRIPE_LIVE_PUBLIC_KEY", default="<your publishable key>")
STRIPE_LIVE_SECRET_KEY = env("STRIPE_LIVE_SECRET_KEY", default="<your secret key>")
STRIPE_TEST_PUBLIC_KEY = env("STRIPE_TEST_PUBLIC_KEY", default="pk_test_<your publishable key>")
STRIPE_TEST_SECRET_KEY = env("STRIPE_TEST_SECRET_KEY", default="sk_test_<your secret key>")
# Change to True in production
STRIPE_LIVE_MODE = env.bool("STRIPE_LIVE_MODE", False)

# djstripe settings
# Get it from the section in the Stripe dashboard where you added the webhook endpoint
# or from the stripe CLI when testing
DJSTRIPE_WEBHOOK_SECRET = env('DJSTRIPE_WEBHOOK_SECRET', default="whsec_xxx")

DJSTRIPE_FOREIGN_KEY_TO_FIELD = 'id'  # change to 'djstripe_id' if not a new installation
DJSTRIPE_USE_NATIVE_JSONFIELD = True  # change to False if not a new installation
DJSTRIPE_SUBSCRIBER_MODEL = 'teams.Team'

# Sentry setup

# populate this to configure sentry. should take the form: 'https://****@sentry.io/12345'
SENTRY_DSN = env('SENTRY_DSN', default='')


if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} "{name}" {message}',
            'style': '{',
            'datefmt': '%d/%b/%Y %H:%M:%S'  # match Django server time format
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
        },
        'bmt_gpt': {
            'handlers': ['console'],
            'level': env('BMT_GPT_LOG_LEVEL', default='INFO'),
        }
    }
}
