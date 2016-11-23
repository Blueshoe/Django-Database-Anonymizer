# Django Database Anonymizer

Management Command to replace privacy-sensitive data with mock data.

This is useful when you want to use nearly-real data and relations in your development and stagings systems. By keeping relations and only replacing defined fields, the development systems keep as close to your live system as possible. 

This approach differs the tool from eg. `django-autofixture`. It is inspired by `django-anonymizer`. 

## Installation & Requirements
To use this tool, just copy this django app in your django project and add it to your `INSTALLED_APPS`.

The package  ```django-bulk-update``` is needed, you can install it via pip:
```
pip install django-bulk-update
```
It is tested in Python 2.7 with Django 1.8

## Management command
```
python manage.py anonymize_db
```
Possible arguments:

* ```-a, --app```: Define a app you want to anonymize. All anonymizers in this app will be run. Eg. ```anonymize_db -a shop.order```
* ```-m, --models```: List of models you want to anonymize. Eg. ```anonymize_db -m Patient,BasketLine
* ```-b, --batch-size```: batch size used in the bulk_update of the instances. Depends on the DB machine. Default is 500.


## Writing anonymizers
In order to use the management command we need to define _**anonymizers**_.

* Create a module _anonymizers.py_ in the given django-app
* An _anonymizer_ is a simple class that inherits from ```BaseAnonymizer```
* Each anonymizer class is going to represent **one** model
* An anonymizer has the following members:
    * ```model```: (required) The model class for this anonymizer
    * ```attributes```: (required) List of tuples that determine which fields to replace. The first value of the tuple is the fieldname, the second value is the _**replacer**_
    * ```get_query_set()```: (optional) Define your QuerySet
* A _replacer_ is either of type _str_ or _callable_
* There are already common replacers defined in ```anonymizer.replacers``` use it for your fields!

#### Example
```
from anonymizer import replacers
from anonymizer.base import BaseAnonymizer
from shop.patient.models import Patient

class PatientAnonymizer(BaseAnonymizer):
    model = Patient

    attributes = [
        ('first_name', 'Dieter'),
        ('last_name', replacers.last_name),

        ('street', replacers.street),
        ('house_number', replacers.random_int),
        ('postcode', replacers.postcode),
        ('city', replacers.city),

        ('phone', replacers.phone),
        ('email', replacers.email),
        ('birth_date', replacers.date),
    ]

    def get_query_set(self):
        return Patient.objects.filter(pk=168460)
```

#### Extending the existing replacers with arguments
Use lambdas to extend certain predefined replacers with arguments, like `length` or `length_range` on `random_string`:
```
('first_name', lambda **kwargs: replacers.random_string(length=5, **kwargs)),
('last_name', lambda **kwargs: replacers.random_string(length_range=(2, 5), **kwargs)),
```
**Important**: don't forget the ****kwargs**!

#### Writing your own replacers
Again, you can use lambdas to write simple custom replacers like:
```
('first_name', lambda **kwargs: 'Vorher war es {}'.format(kwargs.get('field_value'))),
```
The lambda needs to return a string.

If you want to write more complex replacers, you might want to outsource it into its own method:
```
def commission_replacer(**kwargs):
    """
    :type obj: BasketLine
    """
    if isinstance(kwargs.get('instance').basket_group, StockBasketGroup):
        if obj.commission == 'Lager':
            return field  # This is a 'real' stock order, keep it
    # This is a PatientOrder or a StockOrder with probably a patient name as commission
    return replacers.last_name(**kwargs)
```

#### Create new values based on the current value
Sometimes it makes sense to don't add random values to the field, but just change the current value a bit.

Inside the `kwargs` are those two key-value pairs:

* `instance`: The model instance that is about to be anonymized
* `field_value`: The value of the field of the instance that is about to be anonymized. It is a shortcut for `getattr(instance, field_name)`

You can use it like the following to eg. increment the current value by 1
```
def incrementor_replacer(**kwargs):
    return kwargs.get('field_value') + 1
```

## Authors
* [Max Muth](https://github.com/mammuth)
