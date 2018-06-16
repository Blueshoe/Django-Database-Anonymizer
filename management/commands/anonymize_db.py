# -*- coding: utf-8 -*-
import inspect
from importlib import import_module

import sys
import imp as _imp

from django.conf import settings
from django.core.management import BaseCommand

from anonymizer.base import BaseAnonymizer, ANONYMIZER_MODULE_NAME


class Command(BaseCommand):
    help = 'This tool replaces real (user-)data of model instances in your database with mock data.'
    modules = None  # List of anonymizers modules. They can be placed in every app

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--app",
            dest="app",
            help="Only anonymize the given app.",
            metavar="APP"
        ),
        parser.add_argument(
            "-m",
            "--model",
            "--models",
            dest="models",
            help="Models to anonymize. Separate multiples by comma.",
            metavar="MODEL"
        ),
        parser.add_argument(
            "-b",
            "--batch-size",
            dest="batch_size",
            help="batch size used in the bulk_update of the instances. Depends on the DB machine. Use 500 in vagrant.",
            metavar="BATCH_SIZE"
        )

    def handle(self, app, models, batch_size, *args, **options):
        models = None
        if models is not None:
            models = [m.strip() for m in models.split(',')]

        print('Autodiscovering anonymizers')
        modules = self._autodiscover_module(ANONYMIZER_MODULE_NAME, app=app)
        print('Found anonymizers for {} apps'.format(len(modules)))
        total_replacements_count = 0
        for module in modules:
            print('{}:'.format(module.__package__))
            anonymizers = self._get_app_anonymizers(module, models=models)

            if len(anonymizers) == 0:
                print("- No anonymizers or skipped by --app or --model arguments")
                continue

            for anonymizer_class_name in anonymizers:
                anonymizer = getattr(module, anonymizer_class_name)()
                print('- {}'.format(anonymizer.model.__name__))
                number_of_replaced_fields = anonymizer.run(batch_size)  # Start the anonymizing process
                print('-- {} fields, {} model instances, {} total replacements'.format(
                    number_of_replaced_fields[0],
                    number_of_replaced_fields[1],
                    number_of_replaced_fields[2]))
                total_replacements_count += number_of_replaced_fields[2]
        print("DONE. Replaced {} values in total".format(total_replacements_count))

    def _autodiscover_module(self, module_name, app=None):
        apps_to_search = (
            [app]
            if app else
            [x.split(".apps.")[0] for x in settings.INSTALLED_APPS]
        )

        modules = []
        for app in apps_to_search:
            try:
                import_module(app)
                app_path = sys.modules[app].__path__
            except AttributeError:
                continue
            except ImportError:
                print('ERROR: Can not find app ' + app)
                exit(1)
            try:
                _imp.find_module(module_name, app_path)
            except ImportError:
                continue
            import_module('%s.%s' % (app, module_name))
            modules.append(sys.modules['%s.%s' % (app, module_name)])
        return modules

    def _get_app_anonymizers(self, module, models=None):
        if models:
            return [m[0] for m in inspect.getmembers(module, inspect.isclass)
                    if BaseAnonymizer in m[1].__bases__ and m[1].model.__name__ in models]
        else:
            return [m[0] for m in inspect.getmembers(module, inspect.isclass) if BaseAnonymizer in m[1].__bases__]
