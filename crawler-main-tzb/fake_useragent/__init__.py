import re
import string

from datetime import datetime
from collections import OrderedDict

from fake_useragent.distribution import (
    choices_distribution,
    choices_distribution_unique,
)
from fake_useragent.generator import Generator

generator = Generator()
_re_hash = re.compile(r"#")
_re_perc = re.compile(r"%")
_re_excl = re.compile(r"!")
_re_at = re.compile(r"@")
_re_qm = re.compile(r"\?")
_re_cir = re.compile(r"\^")


class BaseProvider:

    __provider__ = "base"
    __use_weighting__ = False
    # Locales supported by Linux Mint from `/usr/share/i18n/SUPPORTED`
    def __init__(self, generator=generator):
        self.generator = generator

    def random_elements(
        self, elements=("a", "b", "c"), length=None, unique=False, use_weighting=None
    ):
        """Generate a list of randomly sampled objects from ``elements``.

        Set ``unique`` to ``False`` for random sampling with replacement, and set ``unique`` to
        ``True`` for random sampling without replacement.

        If ``length`` is set to ``None`` or is omitted, ``length`` will be set to a random
        integer from 1 to the size of ``elements``.

        The value of ``length`` cannot be greater than the number of objects
        in ``elements`` if ``unique`` is set to ``True``.

        The value of ``elements`` can be any sequence type (``list``, ``tuple``, ``set``,
        ``string``, etc) or an ``OrderedDict`` type. If it is the latter, the keys will be
        used as the objects for sampling, and the values will be used as weighted probabilities
        if ``unique`` is set to ``False``. For example:

        .. code-block:: python

            # Random sampling with replacement
            fake.random_elements(
                elements=OrderedDict([
                    ("variable_1", 0.5),        # Generates "variable_1" 50% of the time
                    ("variable_2", 0.2),        # Generates "variable_2" 20% of the time
                    ("variable_3", 0.2),        # Generates "variable_3" 20% of the time
                    ("variable_4": 0.1),        # Generates "variable_4" 10% of the time
                ]), unique=False
            )

            # Random sampling without replacement (defaults to uniform distribution)
            fake.random_elements(
                elements=OrderedDict([
                    ("variable_1", 0.5),
                    ("variable_2", 0.2),
                    ("variable_3", 0.2),
                    ("variable_4": 0.1),
                ]), unique=True
            )

        :sample: elements=('a', 'b', 'c', 'd'), unique=False
        :sample: elements=('a', 'b', 'c', 'd'), unique=True
        :sample: elements=('a', 'b', 'c', 'd'), length=10, unique=False
        :sample: elements=('a', 'b', 'c', 'd'), length=4, unique=True
        :sample: elements=OrderedDict([
                        ("a", 0.45),
                        ("b", 0.35),
                       ("c", 0.15),
                       ("d", 0.05),
                   ]), length=20, unique=False
        :sample: elements=OrderedDict([
                       ("a", 0.45),
                       ("b", 0.35),
                       ("c", 0.15),
                       ("d", 0.05),
                   ]), unique=True
        """
        use_weighting = (
            use_weighting if use_weighting is not None else self.__use_weighting__
        )

        if isinstance(elements, dict) and not isinstance(elements, OrderedDict):
            raise ValueError(
                "Use OrderedDict only to avoid dependency on PYTHONHASHSEED (See #363)."
            )

        fn = choices_distribution_unique if unique else choices_distribution

        if length is None:
            length = self.generator.random.randint(1, len(elements))

        if unique and length > len(elements):
            raise ValueError(
                "Sample length cannot be longer than the number of unique elements to pick from."
            )

        if isinstance(elements, dict):
            if not hasattr(elements, "_key_cache"):
                elements._key_cache = tuple(elements.keys())

            choices = elements._key_cache
            probabilities = tuple(elements.values()) if use_weighting else None
        else:
            if unique:
                # shortcut
                return self.generator.random.sample(elements, length)
            choices = elements
            probabilities = None

        return fn(tuple(choices), probabilities, self.generator.random, length=length,)

    def random_digit(self):
        """Generate a random digit (0 to 9).

        :sample:
        """
        return self.generator.random.randint(0, 9)

    def random_element(self, elements=("a", "b", "c")):
        """Generate a randomly sampled object from ``elements``.

        For information on the ``elements`` argument, please refer to
        :meth:`random_elements() <faker.providers.BaseProvider.random_elements>` which
        is used under the hood with the ``unique`` argument set to ``False`` and the
        ``length`` argument set to ``1``.

        :sample: elements=('a', 'b', 'c', 'd')
        :sample size=10: elements=OrderedDict([
                     ("a", 0.45),
                     ("b", 0.35),
                     ("c", 0.15),
                     ("d", 0.05),
                 ])
        """

        return self.random_elements(elements, length=1)[0]

    def lexify(self, text="????", letters=string.ascii_letters):
        """Generate a string with each question mark ('?') in ``text``
        replaced with a random character from ``letters``.

        By default, ``letters`` contains all ASCII letters, uppercase and lowercase.

        :sample: text='Random Identifier: ??????????'
        :sample: text='Random Identifier: ??????????', letters='ABCDE'
        """
        return _re_qm.sub(lambda x: self.random_element(letters), text)

    def numerify(self, text="###"):
        """Generate a string with each placeholder in ``text`` replaced according
        to the following rules:

        - Number signs ('#') are replaced with a random digit (0 to 9).
        - Percent signs ('%') are replaced with a random non-zero digit (1 to 9).
        - Exclamation marks ('!') are replaced with a random digit or an empty string.
        - At symbols ('@') are replaced with a random non-zero digit or an empty string.

        Under the hood, this method uses :meth:`random_digit() <faker.providers.BaseProvider.random_digit>`,
        :meth:`random_digit_not_null() <faker.providers.BaseProvider.random_digit_not_null>`,
        :meth:`random_digit_or_empty() <faker.providers.BaseProvider.random_digit_or_empty>`,
        and :meth:`random_digit_not_null_or_empty() <faker.providers.BaseProvider.random_digit_not_null_or_empty>`
        to generate the random values.

        :sample: text='Intel Core i%-%%##K vs AMD Ryzen % %%##X'
        :sample: text='!!! !!@ !@! !@@ @!! @!@ @@! @@@'
        """
        text = _re_hash.sub(lambda x: str(self.random_digit()), text)
        text = _re_perc.sub(lambda x: str(self.random_digit_not_null()), text)
        text = _re_excl.sub(lambda x: str(self.random_digit_or_empty()), text)
        text = _re_at.sub(lambda x: str(self.random_digit_not_null_or_empty()), text)
        return text


class Provider(BaseProvider):
    """Implement default user agent provider for Faker."""

    #
    def __init__(self, mobile=False, mobile_type="android"):

        super().__init__()
        self.mobile = mobile
        self.mobile_type = mobile_type

    # windows platform begin from windows NT 6.1 win7
    windows_platform_tokens = (
        "Windows NT 6.1",
        "Windows NT 6.2",
        "Windows NT 10.0",
    )

    linux_processors = ("i686", "x86_64")

    mac_processors = ("Intel", "PPC", "U; Intel", "U; PPC")
    # android version begin from Oreo 2017-7
    android_versions = (
        "8.0.0",
        "8.1.0",
        "9",
        "10",
        "11",
    )
    android_platform = (
        "(Linux; Android 11; V1981A Build/RP1A.200720.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045514 Mobile Safari/537.36",
        "(Linux; U; Android 10; zh-cn; Redmi K20 Pro Build/QKQ1.190825.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/79.0.3945.147 Mobile Safari/537.36 XiaoMi/MiuiBrowser/13.5.40",
        "(Linux; Android 11; SM-G9730 Build/RP1A.200720.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36",
        "(Linux; Android 10; TEL-AN00a; HMSCore 6.0.1.305) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 HuaweiBrowser/11.1.3.300 Mobile Safari/537.36",
        "(Linux; Android 11; M2007J3SC Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045526 Mobile Safari/537.36",
        "(Linux; Android 9; ANE-AL00; HMSCore 6.0.0.305) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 HuaweiBrowser/11.1.3.300 Mobile Safari/537.36",
        "(Linux; Android 10; WLZ-AN00; HMSCore 6.0.1.306) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 HuaweiBrowser/11.1.3.300 Mobile Safari/537.36",
        "(Linux; Android 10; ELE-AL00; HMSCore 6.0.1.306; GMSCore 20.15.16) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 HuaweiBrowser/11.1.3.300 Mobile Safari/537.36",
        "(Linux; Android 10; V2001A Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045710 Mobile Safari/537.36",
        "(Linux; Android 11; SM-G9730 Build/RP1A.200720.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36",
        "(Linux; U; Android 10; zh-cn; Redmi K20 Pro Build/QKQ1.190825.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/79.0.3945.147 Mobile Safari/537.36 XiaoMi/MiuiBrowser/13.5.40",
    )

    apple_devices = ("iPhone", "iPad")

    ios_versions = ("10.3.3", "10.3.4", "12.4.8", "14.2", "14.2.1", "14.6")
    chrome_build_versions = (
        "70.0.3538.16",
        "70.0.3538.67",
        "70.0.3538.97",
        "71.0.3578.137",
        "71.0.3578.30",
        "71.0.3578.33",
        "71.0.3578.80",
        "72.0.3626.69",
        "72.0.3626.7",
        "73.0.3683.20",
        "73.0.3683.68",
        "74.0.3729.6",
        "75.0.3770.140",
        "75.0.3770.8",
        "75.0.3770.90",
        "76.0.3809.12",
        "76.0.3809.126",
        "76.0.3809.25",
        "76.0.3809.68",
        "77.0.3865.10",
        "77.0.3865.40",
        "78.0.3904.105",
        "78.0.3904.11",
        "78.0.3904.70",
        "79.0.3945.16",
        "79.0.3945.36",
        "80.0.3987.106",
        "80.0.3987.16",
        "81.0.4044.138",
        "81.0.4044.20",
        "81.0.4044.69",
        "83.0.4103.14",
        "83.0.4103.39",
        "84.0.4147.30",
        "85.0.4183.38",
        "85.0.4183.83",
        "85.0.4183.87",
        "86.0.4240.22",
        "87.0.4280.20",
        "87.0.4280.87",
        "87.0.4280.88",
        "88.0.4324.27",
        "88.0.4324.96",
        "89.0.4389.23",
        "90.0.4430.24",
        "91.0.4472.101",
        "91.0.4472.19",
        "92.0.4515.43",
    )

    def mac_processor(self):
        """Generate a MacOS processor token used in user agent strings."""
        return self.random_element(self.mac_processors)

    def linux_processor(self):
        """Generate a Linux processor token used in user agent strings."""
        return self.random_element(self.linux_processors)

    def chrome(self):
        """
            if mobile is True: generate ios or android useragent.
            else: generate win or mac desktop useragent.
            Generate a Chrome web browser user agent string.
        """

        saf = f"{self.generator.random.randint(531, 536)}.{self.generator.random.randint(0, 2)}"
        bld = self.lexify(self.numerify("##?###"), string.ascii_uppercase)
        tmplt = "({0}) AppleWebKit/{1} (KHTML, like Gecko)" " Chrome/{2} Safari/{3}"
        tmplt_ios = (
            "({0}) AppleWebKit/{1} (KHTML, like Gecko)"
            " CriOS/{2} Mobile/{3} Safari/{1}"
        )
        # Delete the linux platform to avoid anti-spider.
        if self.mobile:
            # android use collections of colleague's mobile phone.
            if self.mobile_type == "android":
                platforms = self.android_platform
            elif self.mobile_type == "ios":
                platforms = (
                    tmplt_ios.format(
                        self.ios_platform_token(),
                        saf,
                        self.random_element(self.chrome_build_versions),
                        bld,
                    ),
                )
            else:
                platforms = (
                    random.choice(self.android_platform),
                    tmplt_ios.format(
                        self.ios_platform_token(),
                        saf,
                        self.random_element(self.chrome_build_versions),
                        bld,
                    ),
                )
        else:
            platforms = (
                tmplt.format(
                    self.windows_platform_token(),
                    saf,
                    self.random_element(self.chrome_build_versions),
                    saf,
                ),
                tmplt.format(
                    self.mac_platform_token(),
                    saf,
                    self.random_element(self.chrome_build_versions),
                    saf,
                ),
            )

        return "Mozilla/5.0 " + self.random_element(platforms)

    def windows_platform_token(self):
        """Generate a Windows platform token used in user agent strings."""
        return self.random_element(self.windows_platform_tokens)

    def mac_platform_token(self):
        """Generate a MacOS platform token used in user agent strings."""
        return (
            f"Macintosh; {self.random_element(self.mac_processors)} Mac OS X 10 "
            f"{self.generator.random.randint(5, 12)}_{self.generator.random.randint(0, 9)}"
        )

    def android_platform_token(self):
        """Generate an Android platform token used in user agent strings."""
        return f"Android {self.random_element(self.android_versions)}"

    def ios_platform_token(self):
        """Generate an iOS platform token used in user agent strings."""
        apple_device = self.random_element(self.apple_devices)
        return (
            f"{apple_device}; CPU {apple_device} "
            f'OS {self.random_element(self.ios_versions).replace(".", "_")} like Mac OS X'
        )
