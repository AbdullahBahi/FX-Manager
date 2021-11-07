from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    setup(name = 'FX-Manager',
        version = '1.0.12',
        author = 'Abdullah Bahi',
        author_email = 'abdullahbahi@icloud.com',
        description = 'Python package for developing and testing forex algorithmic trading strategies.',
        long_description = long_description,
        long_description_content_type = "text/markdown",
        url = 'https://github.com/AbdullahBahi/fxmanager',
        classifiers = ['Development Status :: 3 - Alpha',
                        'Intended Audience :: Developers',
                        'Topic :: Software Development :: Build Tools',
                        'License :: OSI Approved :: GNU General Public License (GPL)',
                        'Programming Language :: Python :: 3',
                        'Operating System :: OS Independent'],
        keywords = ['forex', 'forex trading', 'algorethmic trading', 'backtesting'],
        scripts = ['scripts\\create_fx_proj.py',
                        'scripts\\fx_data_collector.py', 
                        'scripts\\fx_pp.py',
                        'scripts\\run_fx_hist_sim.py', 
                        'scripts\\run_fx_live_sim.py', 
                        'scripts\\run_fx_opt_test.py'],
        package_dir = {'':'src'},
        packages = find_packages(where='src'),
        install_requires = ['zmq',
                        'pandas>=0.25.1',
                        'numpy>=1.16.5',
                        'matplotlib>=3.1.1'],
        python_requires = '>=3.7'
    )
except:
    print('Error!')
