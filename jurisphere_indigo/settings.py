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

# boto3 defaults to sending/validating checksum headers that GCS's S3-compatible API rejects.
# botocore reads these from the environment when it builds a client, so setting them here (rather
# than requiring them at deploy time) is enough as long as it happens before the first S3 call.
os.environ.setdefault("AWS_REQUEST_CHECKSUM_CALCULATION", "when_required")
os.environ.setdefault("AWS_RESPONSE_CHECKSUM_VALIDATION", "when_required")

# Origins allowed to submit forms besides the service's own host. Access through
# `gcloud run services proxy` arrives with Origin http://localhost:8080 while Django sees the
# run.app host, so CSRF rejects it unless that origin is trusted.
CSRF_TRUSTED_ORIGINS = os.environ["CSRF_TRUSTED_ORIGINS"].split(",")

# Accounts are created by an admin. The signup form rejects submissions, so its reCAPTCHA
# (Indigo's default Google test keys) is never relied on.
ACCOUNT_SIGNUP_ENABLED = False
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]

# No SMTP server is configured; log outgoing email instead of failing the request.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
