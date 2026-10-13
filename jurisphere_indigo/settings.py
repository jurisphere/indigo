"""Jurisphere deployment settings, layered on Indigo's defaults.

Selected with DJANGO_SETTINGS_MODULE=jurisphere_indigo.settings.
"""

import os

from indigo.settings import *  # noqa: F401,F403
from indigo.settings import STORAGES as BASE_STORAGES

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

# Attachments use the Cloud Run runtime service account's GCS permissions.
STORAGES = {
    **BASE_STORAGES,
    "default": {"BACKEND": "storages.backends.gcloud.GoogleCloudStorage"},
}
GS_BUCKET_NAME = os.environ["GS_BUCKET_NAME"]
GS_FILE_OVERWRITE = False

# Comma-separated hostnames this deployment serves.
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")

# Comma-separated origins allowed to submit forms.
CSRF_TRUSTED_ORIGINS = os.environ["CSRF_TRUSTED_ORIGINS"].split(",")

# Accounts are created by an admin. The signup form rejects submissions, so its reCAPTCHA
# (Indigo's default Google test keys) is never relied on.
ACCOUNT_SIGNUP_ENABLED = False
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]

# No SMTP server is configured; log outgoing email instead of failing the request.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
