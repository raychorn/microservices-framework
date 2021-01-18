"""
Django settings for microservices_framework project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

import os, sys
from os import environ
from pathlib import Path

def getVersionID():
    import sys
    return '{}{}'.format(int(sys.version_info.major), int(sys.version_info.minor))

BASE_DIR = Path(__file__).resolve().parent
if (DEBUG):
    print('DEBUG: BASE_DIR -> {}.'.format(BASE_DIR))

# BEGIN: This is required. This covers all the bases for deployment. Your deployment might differ but this was mine.
pylib3 = os.sep.join([os.path.dirname(BASE_DIR), 'python_lib3', 'vyperlogix{}.zip'.format(getVersionID())])
if (not os.path.exists(pylib3)):
    pylib3 = os.path.dirname(pylib3)
    assert os.path.exists(pylib3) and os.path.isdir(pylib3), 'Problem. Cannot find development {} in {}.'.format(os.path.basename(pylib3), os.path.dirname(pylib3))
else:
    assert os.path.exists(pylib3) and os.path.isfile(pylib3), 'Problem. Cannot find deployment {} in {}.'.format(os.path.basename(pylib3), os.path.dirname(pylib3))
sys.path.insert(0, pylib3)
pylib3a = os.sep.join([pylib3, 'private_vyperlogix_lib3'])
if (os.path.exists(pylib3a) and os.path.isdir(pylib3a)):
    sys.path.insert(0, pylib3a)
# END!!! This is required.

if (DEBUG):
    print('BEGIN: PYTHONPATH')
    for f in sys.path:
        print(f)
    print('END!!! PYTHONPATH')

import json
from vyperlogix.misc import _utils
from vyperlogix.env import environ
from vyperlogix.crypto import utils as crypto_utils

# Build paths inside the project like this: BASE_DIR / 'subdir'.
__version = _utils.getVersionFloat()
assert (__version >= 3.00) and (__version < 3.90), 'Incompatible Python Version. Must use Python 3.x or later. __version -> {}'.format(__version)

import traceback

__secrets = os.environ.get('SECRETS', '').split(',')

__env_keys = []
def get_environ_keys(*args, **kwargs):
    '''
    this handles the oddly placed .env file the runtime will find and use rather than place the .env file where the runtime would notmally expect to see it.
    secrets are encrypted.  Use crypto_utils.encrypt(v) to form encrypted values.
    '''
    global __secrets
    k = kwargs.get('key')
    v = kwargs.get('value')
    verbose = kwargs.get('verbose', False)
    assert (k is not None) and (v is not None), 'Problem with kwargs -> {}, k={}, v={}'.format(kwargs,k,v)
    environ = kwargs.get('environ', {})
    __env_keys.append(k)
    if (environ.get(k) == None):
        environ[k] = v
    if (k == 'SECRETS'):
        for t in v.split(','):
            __secrets.append(t)
        __secrets = list(set([t for t in __secrets if (len(t.strip()) > 0)]))
        if (verbose):
            print('\t__secrets -> {}'.format(__secrets))
    vv = v
    if (_utils.is_hex_str(v)) and (k in __secrets):
        vv = crypto_utils.decrypt(v)
        __env_keys.append(k)
        v = vv
        if (verbose):
            print('\tv -> {}'.format(v))
    if (verbose):
        print('\t{} -> {}'.format(k, v))
    environ[k] = v
    return True

env_path = os.sep.join([os.path.dirname(BASE_DIR), '.env'])
print('*** env_path -> {}'.format(env_path))
assert os.path.exists(env_path) and os.path.isfile(env_path), 'Problem with {}'.format(env_path)
environ.load_env(env_path=env_path, environ=os.environ, cwd=os.path.dirname(BASE_DIR), verbose=True, ignoring_re='.git|.venv|__pycache__', callback=lambda *args, **kwargs:get_environ_keys(args, **kwargs))

from vyperlogix.mongo import vyperapi
from vyperlogix.decorators import __with
from vyperlogix.json import db

__tmp__ = '/tmp/{}'.format(str(BASE_DIR).split(os.sep)[-1])
if (not os.path.exists(__tmp__)):
    os.mkdir(__tmp__)
print('DEBUG: __tmp__ -> {}'.format(__tmp__))

if (0):
    @__with.redirect_stdout_to(__tmp__)
    def print_environ(file=None):
        print('BEGIN: __env_keys', file=file)
        for k in __env_keys:
            print('{}'.format(k), file=file)
        print('END!!! __env_keys', file=file)
        print('='*30, file=file)
        print('', file=file)
        print('BEGIN: os.environ', file=file)
        for k,v in os.environ.items():
            if (k in __env_keys):
                print('"{}" -> "{}"'.format(k,v), file=file)
        print('END!!! os.environ', file=file)
        print('='*30, file=file)
        print('', file=file)
    print('BEGIN:')
    print_environ()
    print('END!!!')

admin_id = os.environ.get('ADMIN_ID')
assert len(admin_id) > 0, 'Missing ADMIN_ID ({}). Please add one to the .env file.'.format(admin_id)

doc = vyperapi.auto_config_admin(mongouri=os.environ.get('MONGO_URI'), db_name=os.environ.get('MONGO_INITDB_DATABASE'), app_dbName=os.environ.get('ADMIN_TABLE'), app_colName=os.environ.get('ADMIN_COL'), user_type='admin', admin_id=admin_id, username=os.environ.get('MONGO_INITDB_ROOT_USERNAME'), password=os.environ.get('MONGO_INITDB_ROOT_PASSWORD'), authMechanism=os.environ.get('MONGO_AUTH_MECHANISM'), verbose=False, debug=False, report_except=True)
assert doc.get('admin') == admin_id, 'Cannot find ADMIN_ID in db ({}). Please fix.'.format(doc)

@__with.database()
def check_admin_user(db=None):
    tb_name = os.environ.get('ADMIN_TABLE')
    assert vyperapi.is_valid_str(tb_name), 'Failed to get ADMIN_TABLE -> {}'.format(tb_name)
    col_name = os.environ.get('ADMIN_COL')
    assert vyperapi.is_valid_str(col_name), 'Failed to get ADMIN_COL -> {}'.format(col_name)
    assert db, 'create_admin_user() was not called properly. There is no db context.'
    table = db[tb_name]
    col = table[col_name]

    print('*** create_admin_user (2.1) tb_name -> {}'.format(tb_name))
    print('*** create_admin_user (2.2) table -> {}'.format(table))
    print('*** create_admin_user (2.3) col_name -> {}'.format(col_name))
    print('*** create_admin_user (2.4) col -> {}'.format(col))

    __doc = col.find_one({'admin': doc.get('admin')})
    assert __doc.get('admin') == doc.get('admin'), 'Cannot verify admin_id in db.'

print('*** BEGIN: check_admin_user')
check_admin_user()
print('*** END!!! check_admin_user')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'bz$h33y1n&p-%_10ko@1dtaf$ys1la7xpi)0thw+t_zm&04r!-'

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'POST',
    'PUT',
]

ADMINS = (
    ('Admin', 'no-reply@vyperlogix.com'),
)

MANAGERS = ADMINS
# Application definition

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'microservices_framework.views',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_json_404_middleware.JSON404Middleware',
]

ROOT_URLCONF = 'microservices_framework.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
print('DEBUG: TEMPLATES_DIR -> {} exists -> {}.'.format(TEMPLATES_DIR, os.path.exists(TEMPLATES_DIR) and os.path.isdir(TEMPLATES_DIR)))

from vyperlogix.django.findDjangoTemplateDirsIn import findDjangoTemplateDirsIn
TEMPLATES_DIR = findDjangoTemplateDirsIn([TEMPLATES_DIR,], dir_name=BASE_DIR, contains='templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATES_DIR,
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

WSGI_APPLICATION = 'microservices_framework.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR , 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
print('STATICFILES_DIRS -> {}'.format(STATICFILES_DIRS))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },    
    'handlers': {
        'logit': {
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/log/django/{}.log'.format(str(BASE_DIR).split(os.sep)[-1]),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'verbose',
        },        
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logit', 'console'],
            'propagate': True,
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
        },
    },
}    