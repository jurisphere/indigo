import os
import subprocess
import sys
from unittest import TestCase


class DeploymentSettingsTestCase(TestCase):
    def test_native_gcs_with_runtime_credentials(self):
        environment = {
            **os.environ,
            'DJANGO_SETTINGS_MODULE': 'jurisphere_indigo.settings',
            'DJANGO_DEBUG': 'false',
            'DJANGO_SECRET_KEY': 'test-signing-key',
            'DB_HOST': '/cloudsql/test-instance',
            'DB_NAME': 'indigo',
            'DB_USER': 'indigo',
            'DB_PASSWORD': 'test-password',
            'GS_BUCKET_NAME': 'test-indigo-bucket',
            'ALLOWED_HOSTS': 'indigo.jurisphere.ai',
            'CSRF_TRUSTED_ORIGINS': 'https://indigo.jurisphere.ai',
        }
        for key in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_S3_BUCKET', 'SENTRY_DSN'):
            environment.pop(key, None)
        subprocess.run([sys.executable, '-c', """
from unittest.mock import patch
from django.core.files.storage import storages
from indigo.settings import STORAGES as upstream_storages
from jurisphere_indigo import settings
from storages.backends.gcloud import GoogleCloudStorage

assert settings.DEBUG is False
assert settings.STORAGES['staticfiles'] == upstream_storages['staticfiles']
assert settings.STORAGES['default']['BACKEND'] == 'storages.backends.gcloud.GoogleCloudStorage'
backend = storages['default']
assert isinstance(backend, GoogleCloudStorage)
assert backend.file_overwrite is False
with patch('storages.backends.gcloud.Client') as client:
    backend.bucket
    client.return_value.bucket.assert_called_once_with('test-indigo-bucket')
"""], env=environment, check=True)

    def test_bucket_name_is_required(self):
        environment = {
            **os.environ,
            'DB_HOST': '/cloudsql/test-instance',
            'DB_NAME': 'indigo',
            'DB_USER': 'indigo',
            'DB_PASSWORD': 'test-password',
        }
        environment.pop('GS_BUCKET_NAME', None)
        result = subprocess.run(
            [sys.executable, '-c', 'import jurisphere_indigo.settings'],
            env=environment, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("KeyError: 'GS_BUCKET_NAME'", result.stderr)
