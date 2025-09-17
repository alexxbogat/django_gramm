from .base_settings import *

DEBUG = False

ALLOWED_HOSTS = ['heroic-oven-469018-n1.ew.r.appspot.com']

GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME')
GS_PROJECT_ID = os.getenv('GS_PROJECT_ID')
GS_CUSTOM_ENDPOINT = f'https://storage.googleapis.com/{GS_BUCKET_NAME}'
STATIC_URL = f'{GS_CUSTOM_ENDPOINT}/'
GS_DEFAULT_ACL = 'publicRead'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT", "5432"),
    }
}

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "project_id": GS_PROJECT_ID,
            "bucket_name": GS_BUCKET_NAME,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "project_id": GS_PROJECT_ID,
            "bucket_name": GS_BUCKET_NAME,
        },
    },
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
