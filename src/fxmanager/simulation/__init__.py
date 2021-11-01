"""
This sub-package contains the modules used for historical and live trading sumulations.

Modules:
    - historic: This module contains helper functions used internally in this module and a public function to run historical simulation.
    
    - live    : This module contains helper functions used internally in this module and a public function to run live simulation with live price feed from MT4.
"""

from . import historic
from . import live
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)