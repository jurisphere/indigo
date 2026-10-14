import sys
from unittest.mock import patch

from django.apps import apps
from django.test import SimpleTestCase, override_settings


class IndigoApiStartupTestCase(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_migrate_does_not_schedule_pruning(self):
        with patch.object(sys, 'argv', ['manage.py', 'migrate']), \
                patch('indigo_api.tasks.setup_pruning') as setup_pruning:
            apps.get_app_config('indigo_api').ready()
        setup_pruning.assert_not_called()

    @override_settings(DEBUG=False)
    def test_web_startup_schedules_pruning(self):
        with patch.object(sys, 'argv', ['gunicorn', 'indigo.wsgi']), \
                patch('indigo_api.tasks.setup_pruning') as setup_pruning:
            apps.get_app_config('indigo_api').ready()
        setup_pruning.assert_called_once_with()
