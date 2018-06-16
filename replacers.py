# -*- coding: utf-8 -*-
import string
import random
from datetime import datetime

from anonymizer.data import companies as _data_companies
from .data.de import last_names as _data_last_names, first_names as _data_first_names, cities as _data_cities


def boolean(**kwargs):
    return bool(random.getrandbits(1))


def full_name(**kwargs):
    return "%s %s" % (first_name(**kwargs), last_name(**kwargs), )


def first_name(**kwargs):
    return random.choice(_data_first_names)


def last_name(**kwargs):
    return random.choice(_data_last_names)


def street(**kwargs):
    return last_name(**kwargs) + random.choice(['-Straße', 'straße', '-Weg', 'weg'])


def city(**kwargs):
    return random.choice(_data_cities)


def postcode(**kwargs):
    return random_int(range=(1000, 97999), **kwargs)


def phone(**kwargs):
    return random_int(range=(100000, 9999999999), **kwargs)


def email(**kwargs):
    return '{}.{}@blueshoe-testdata.de'.format(first_name(**kwargs), last_name(**kwargs))


def date(**kwargs):
    year = random.choice(range(1950, 2016))
    month = random.choice(range(1, 13))
    day = random.choice(range(1, 29))
    return datetime(year, month, day)


def company_name(**kwargs):
    return random.choice(_data_companies)


def random_string(length=5, length_range=None, capitalized=True, **kwargs):
    """
    Returns a random capitalized string

    If you want to modify the parameters, use a lambda function in your anonymizer like this:
    attributes = [
        ('first_name', lambda **kwargs: replacers.random_string(length_range=(2, 6), **kwargs)),
    ]

    :param length: The wished length of the random string
    :param length_range: Tuple with the wished length range of the random string. ONLY USE length OR length_range!
    :param capitalized: Whether the string should be capitalized
    :return: Random string with the specified params
    """
    if length_range is not None:
        result = ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randrange(*length_range)))
    else:
        result = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
    return result.capitalize() if capitalized else result


def random_int(range=None, **kwargs):
    """

    :param obj: model instance
    :param field: instance field
    :param range: range of the random integer. Type: Tuple
    :return:
    """
    if range is None:
        return int(random.random() * 100)
    else:
        return random.randint(*range)
