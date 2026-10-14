import sys

from django.apps import AppConfig
from django.conf import settings


class IndigoApiConfig(AppConfig):
    name = 'indigo_api'
    verbose_name = 'Indigo API'

    def ready(self):
        from actstream import registry
        from django.contrib.auth.models import User
        from indigo_api.models import Amendment, Document, Task, Work, PlaceSettings, ArbitraryExpressionDate, Commencement
        import indigo_api.importers.base # noqa

        registry.register(Amendment)
        registry.register(Document)
        registry.register(Task)
        registry.register(User)
        registry.register(Work)
        registry.register(PlaceSettings)
        registry.register(ArbitraryExpressionDate)
        registry.register(Commencement)

        # Migrations create the tables used by the pruning scheduler.
        if not settings.DEBUG and sys.argv[1:2] != ['migrate']:
            from indigo_api.tasks import setup_pruning
            setup_pruning()
