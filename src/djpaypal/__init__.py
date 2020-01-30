import pkg_resources
from . import checks  # noqa: Register the checks


__version__ = pkg_resources.require("dj-paypal")[0].version
