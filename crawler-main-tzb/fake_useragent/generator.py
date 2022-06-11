import random as random_module
import re
from calendar import timegm
from datetime import MAXYEAR, date, datetime, timedelta

from dateutil import relativedelta
from dateutil.tz import gettz, tzlocal, tzutc

_re_token = re.compile(r"\{\{\s*(\w+)(:\s*\w+?)?\s*\}\}")
random = random_module.Random()
mod_random = random  # compat with name released in 0.8


def datetime_to_timestamp(dt):
    if getattr(dt, "tzinfo", None) is not None:
        dt = dt.astimezone(tzutc())
    return timegm(dt.timetuple())


class Generator:

    __config = {
        "arguments": {},
    }

    def __init__(self, **config):
        self.providers = []
        self.__config = dict(list(self.__config.items()) + list(config.items()))
        self.__random = random

    @classmethod
    def _parse_date_time(cls, value, tzinfo=None):
        if isinstance(value, (datetime, date)):
            return datetime_to_timestamp(value)
        now = datetime.now(tzinfo)
        if isinstance(value, timedelta):
            return datetime_to_timestamp(now + value)
        if isinstance(value, str):
            if value == "now":
                return datetime_to_timestamp(datetime.now(tzinfo))
            time_params = cls._parse_date_string(value)
            return datetime_to_timestamp(now + timedelta(**time_params))
        if isinstance(value, int):
            return datetime_to_timestamp(now + timedelta(value))
        raise ParseError(f"Invalid format for date {value!r}")

    @classmethod
    def _parse_date(cls, value):
        if isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            return value
        today = date.today()
        if isinstance(value, timedelta):
            return today + value
        if isinstance(value, str):
            if value in ("today", "now"):
                return today
            time_params = cls._parse_date_string(value)
            return today + timedelta(**time_params)
        if isinstance(value, int):
            return today + timedelta(value)
        raise ParseError(f"Invalid format for date {value!r}")

    def date_time_between(self, start_date="-30y", end_date="now", tzinfo=None):
        """
        Get a DateTime object based on a random date between two given dates.
        Accepts date strings that can be recognized by strtotime().

        :param start_date Defaults to 30 years ago
        :param end_date Defaults to "now"
        :param tzinfo: timezone, instance of datetime.tzinfo subclass
        :example DateTime('1999-02-02 11:42:52')
        :return DateTime
        """
        start_date = self._parse_date_time(start_date, tzinfo=tzinfo)
        end_date = self._parse_date_time(end_date, tzinfo=tzinfo)
        if end_date - start_date <= 1:
            ts = start_date + self.generator.random.random()
        else:
            ts = self.generator.random.randint(start_date, end_date)
        if tzinfo is None:
            return datetime(1970, 1, 1, tzinfo=tzinfo) + timedelta(seconds=ts)
        else:
            return (
                datetime(1970, 1, 1, tzinfo=tzutc()) + timedelta(seconds=ts)
            ).astimezone(tzinfo)

    def add_provider(self, provider):

        if isinstance(provider, type):
            provider = provider(self)

        self.providers.insert(0, provider)

        for method_name in dir(provider):
            # skip 'private' method
            if method_name.startswith("_"):
                continue

            faker_function = getattr(provider, method_name)

            if callable(faker_function):
                # add all faker method to generator
                self.set_formatter(method_name, faker_function)

    def provider(self, name):
        try:
            lst = [p for p in self.get_providers() if p.__provider__ == name.lower()]
            return lst[0]
        except IndexError:
            return None

    def get_providers(self):
        """Returns added providers."""
        return self.providers

    @property
    def random(self):
        return self.__random

    @random.setter
    def random(self, value):
        self.__random = value

    def seed_instance(self, seed=None):
        """Calls random.seed"""
        if self.__random == random:
            # create per-instance random obj when first time seed_instance() is
            # called
            self.__random = random_module.Random()
        self.__random.seed(seed)
        return self

    @classmethod
    def seed(cls, seed=None):
        random.seed(seed)

    def format(self, formatter, *args, **kwargs):
        """
        This is a secure way to make a fake from another Provider.
        """
        return self.get_formatter(formatter)(*args, **kwargs)

    def get_formatter(self, formatter):
        try:
            return getattr(self, formatter)
        except AttributeError:
            if "locale" in self.__config:
                msg = f'Unknown formatter {formatter!r} with locale {self.__config["locale"]!r}'
            else:
                raise AttributeError(f"Unknown formatter {formatter!r}")
            raise AttributeError(msg)

    def set_formatter(self, name, method):
        """
        This method adds a provider method to generator.
        Override this method to add some decoration or logging stuff.
        """
        setattr(self, name, method)

    def set_arguments(self, group, argument, value=None):
        """
        Creates an argument group, with an individual argument or a dictionary
        of arguments. The argument groups is used to apply arguments to tokens,
        when using the generator.parse() method. To further manage argument
        groups, use get_arguments() and del_arguments() methods.

        generator.set_arguments('small', 'max_value', 10)
        generator.set_arguments('small', {'min_value': 5, 'max_value': 10})
        """
        if group not in self.__config["arguments"]:
            self.__config["arguments"][group] = {}

        if isinstance(argument, dict):
            self.__config["arguments"][group] = argument
        elif not isinstance(argument, str):
            raise ValueError("Arguments must be either a string or dictionary")
        else:
            self.__config["arguments"][group][argument] = value

    def get_arguments(self, group, argument=None):
        """
        Get the value of an argument configured within a argument group, or
        the entire group as a dictionary. Used in conjunction with the
        set_arguments() method.

        generator.get_arguments('small', 'max_value')
        generator.get_arguments('small')
        """
        if group in self.__config["arguments"] and argument:
            result = self.__config["arguments"][group].get(argument)
        else:
            result = self.__config["arguments"].get(group)

        return result

    def del_arguments(self, group, argument=None):
        """
        Delete an argument from an argument group or the entire argument group.
        Used in conjunction with the set_arguments() method.

        generator.del_arguments('small')
        generator.del_arguments('small', 'max_value')
        """
        if group in self.__config["arguments"]:
            if argument:
                result = self.__config["arguments"][group].pop(argument)
            else:
                result = self.__config["arguments"].pop(group)
        else:
            result = None

        return result

    def parse(self, text):
        """
        Replaces tokens like '{{ tokenName }}' or '{{tokenName}}' in a string with
        the result from the token method call. Arguments can be parsed by using an
        argument group. For more information on the use of argument groups, please
        refer to the set_arguments() method.

        Example:

        generator.set_arguments('red_rgb', {'hue': 'red', 'color_format': 'rgb'})
        generator.set_arguments('small', 'max_value', 10)

        generator.parse('{{ color:red_rgb }} - {{ pyint:small }}')
        """
        return _re_token.sub(self.__format_token, text)

    def __format_token(self, matches):
        formatter, argument_group = list(matches.groups())
        argument_group = argument_group.lstrip(":").strip() if argument_group else ""

        if argument_group:
            try:
                arguments = self.__config["arguments"][argument_group]
            except KeyError:
                raise AttributeError(f"Unknown argument group {argument_group!r}")

            formatted = str(self.format(formatter, **arguments))
        else:
            formatted = str(self.format(formatter))

        return "".join(formatted)
