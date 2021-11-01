"""
This sub-package contains the mudules used for building and injecting trading strategies int FX-Manager's trading simulations.

Public Modules:
    - naieve_momentum: This module contains simple implementation of momentum trading strategy, used as default for simulations.
"""

from . import naieve_momentum
from . import template
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)