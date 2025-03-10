from importlib.metadata import version

from . import checks  # noqa: Register the checks


__version__ = version("dj-paypal")
