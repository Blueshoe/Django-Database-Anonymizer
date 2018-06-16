# -*- coding: utf-8 -*-
from bulk_update.helper import bulk_update

ANONYMIZER_MODULE_NAME = 'anonymizers'
DEFAULT_CHUNK_SIZE = 500


class BaseAnonymizer:

    def __init__(self):
        try:
            getattr(self, 'model')
            getattr(self, 'attributes')
        except AttributeError:
            print('ERROR: Your anonymizer is missing the model or attributes definition!')
            exit(1)

    def get_query_set(self):
        """
        You can override this in your Anonymizer.
        :return: QuerySet
        """
        return self.model.objects.all()

    def run(self, batch_size=None):
        count_instances = 0
        count_fields = 0
        instances = self.get_query_set()
        for model_instance in instances:
            for field_name, replacer in self.attributes:
                field_value = getattr(model_instance, field_name)
                if callable(replacer):
                    replaced_value = replacer(instance=model_instance, field_value=field_value)
                elif isinstance(replacer, basestring):
                    replaced_value = replacer
                else:
                    raise TypeError('Replacers need to be callables or Strings!')
                setattr(model_instance, field_name, replaced_value)
                count_fields += 1
            count_instances += 1
        batch_size = DEFAULT_CHUNK_SIZE if batch_size is None else int(batch_size)
        bulk_update(instances, update_fields=[attrs[0] for attrs in self.attributes], batch_size=batch_size)
        return len(self.attributes), count_instances, count_fields
