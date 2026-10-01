"""Jurisphere deployment settings, layered on Indigo's defaults.

Selected with DJANGO_SETTINGS_MODULE=jurisphere_indigo.settings.
"""

import os

from indigo.settings import *  # noqa: F403

# Postgres from discrete variables; DB_HOST may be a Cloud SQL socket directory (/cloudsql/<instance>).
# Indigo routes server-side-cursor queries through "direct"; with no pooler it is the same connection.
_database = {
    "ENGINE": "django.db.backends.postgresql",
    "HOST": os.environ["DB_HOST"],
    "NAME": os.environ["DB_NAME"],
    "USER": os.environ["DB_USER"],
    "PASSWORD": os.environ["DB_PASSWORD"],
}
DATABASES = {"default": _database, "direct": _database}

# Attachments live in GCS, accessed through its S3-compatible API with an HMAC key
# (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_S3_BUCKET from the environment).
AWS_S3_ENDPOINT_URL = "https://storage.googleapis.com"
AWS_S3_REGION_NAME = "auto"

# No SMTP server is configured; log outgoing email instead of failing the request.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
