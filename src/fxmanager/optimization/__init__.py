"""
This sub-package contains the mudules used for portfolio construction and optimization.

Modules:
    - eq_weight_optimizer   : This module contains helper functions used internally in this module and other  modules in fxmanager's optimization sub-package. 
    
    - eqw_optimization_test : This module contains a function that rans an equally weighted optimization test on historical data.

    - weight_optimizer      : This module contains a function that rans a weighted optimization test on historical data.

    - w_optimization_test   : This module contains helper functions used internally in this module and other modules in fxmanager's optimization sub-package. 
"""

from . import eq_weight_optimizer
from . import eqw_optimization_test
from . import w_optimization_test
from . import weight_optimizer
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)