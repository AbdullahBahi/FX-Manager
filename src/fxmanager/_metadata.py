__package_name__                 = 'FX-Manager'
__version__                      = '1.0.15'
__author__                       = 'Abdullah Bahi'
__author_email__                 = 'abdullahbahi@icloud.com'
__description__                  = 'Python package for developing and testing forex algorithmic trading strategies.'
__long_description_content_type__= "text/markdown"
__url__                          = 'https://github.com/AbdullahBahi/fxmanager'
__keywords__                     = ['forex', 'forex trading', 'algorethmic trading', 'backtesting']
__python_requires__              = '>=3.7'
__copyright__                    = "Copyright © 2021 Abdullah Bahi"
__credits__                      = ["Darwinex"]
__license__                      = "GNU General Public License (GPL)"
__maintainer__                   = "Abdullah Bahi"
__status__                       = "3 - Alpha"

__classifiers__      = ['Development Status :: 3 - Alpha',
                        'Intended Audience :: Developers',
                        'Topic :: Software Development :: Build Tools',
                        'License :: OSI Approved :: GNU General Public License (GPL)',
                        'Programming Language :: Python :: 3',
                        'Operating System :: OS Independent']

__scripts__          = ['scripts\\historical_simulation.py',
                        'scripts\\live_simulation.py', 
                        'scripts\\optimizer_test.py',
                        'scripts\\pp.py', 
                        'scripts\\setup.py', 
                        'scripts\\test_rates_historic.py']

__package_dir__      = {'':'src'}

__packages__         = ['fxmanager', 'fxmanager.basic', 'fxmanager.dwx', 'fxmanager.optimization', 'fxmanager.simulation', 'fxmanager.strategies']

__install_requires__ =['zmq',
                        'pandas>=0.25.1',
                        'numpy>=1.16.5',
                        'matplotlib>=3.1.1']

