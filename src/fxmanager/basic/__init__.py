"""
This sub-package contains mudules of helper functions used intrnally in all FX-Manager's sub-packages.

in addition to the helper functions, the sub-package contains functions used for setting up new FX-Manager projects and preprocessing data to be compaitable with FX-Manager. it also contains the module used for simulating the trading accounts.

Modules:
    - util    : This module contains helper functions used internally in other fxmanager sub-packages. it also includes public functions to be used by the user to setup fxmanager project structure and pre-process the data.

    - account : This module contains 'Account' class which is used for creating a fully functional virtual forex trading accounts.
"""

from . import util
from . import account
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)