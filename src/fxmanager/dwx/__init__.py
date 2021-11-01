"""
This sub-package contains a modified version of Darwinex ZeroMQ connector which is used for connecting client code to MT4 trading platform.

Public Modules:
    - prices_subscription : This is a modified version of an example of using the Darwinex ZeroMQ Connector for Python 3 and MT4 PULL REQUEST.
    - rates_historic      : This Module is used as an API to get historic data from the MT4 EA.
"""

from . import prices_subscriptions
from . import rates_historic
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)