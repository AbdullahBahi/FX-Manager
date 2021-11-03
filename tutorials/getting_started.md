# Getting Started With FX-Manager
This guild shows the basic usage of FX-Manager, for further details on the different functionalities of the package, follow the other tutorials listed [here](https://fx-manager.readthedocs.io/en/latest/tutorials.html). 
> **Delimiter:** make sure you have followed the step-by-step Installation guild before proceeding in this tutorial.
## Contents
- [Introduction](#Introduction)
- [Using the built-in commands](#Using-the-built-in-commands )
	- [Pre-configuration](#Pre-configuration)
- [Creating a new FX-Manager project](#Creating-a-new-FX-Manager-project)
- [Next steps](#Next-steps)

## Introduction
Fx-Manager framework is mainly used to create client server applications where the client is the trading bot written in python using FX-Manager’s APIs, and the server is an expert advisor that is installed on MT4 trading platform.

The following block diagram demonstrates how how FX-Manager works.

![FX-Manager Block Diagram](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/1.png)

As shown above, FX-Manager offers a variety of services that can be very useful for any algorithmic trader. See [Features](https://fx-manager.readthedocs.io/en/latest/features.html) section for more details on how each service  works.


## Using the built-in commands
FX-Manager comes with built in scripts that can be used directly as system commands from user's Command line Interface(CLI). This makes user experience much more easier and time efficient. This list shows all the available scripts:
- **fx_data_collector** : This script is used for collecting data from MT4 history center.
- **create_fx_proj** : This script is used for setting up a new FX-Manager project.
- **fx_pp** : This script is used for pre-processing raw market prices data to be compaitable with FX-Manager.
- **run_fx_opt_test** : This script runs a portfolio optimization test using historical data.
- **run_fx_hist_sim** : This script is used for running a historical trading simulation with historical prices.
- **run_fx_live_sim** : This script is used for running a live trading simulation with real market prices from MT4 platform.
> for more details on how to use each script, make the required pre-configurations below, then run the following command from your CLI:
> `script_name --help`
> replace **script_name** with the script's name. 

### Pre-configuration
To get these scripts to work properly, the following configurations needs to be made.
- make make `python.exe` the default application to run `.py` files. This can be done manually as follows:
	> Right click on the file > open with > chose another app > navigate to "C:\Users\User\Anaconda3" and select **python.exe** > check "always use this app to open .py files" and click **ok**.
- from a CLI window, run the following commands:
`assoc .py=pyautofile`
`ftype pyautofile="full_path_to_python.exe" "%1" %*`

- open start menu and search for `Registry editor`, then navigate to:
	```
	HKEY_CLASSES_ROOT\Applications\python.exe\shell\open\command
	```
	and change it's value to:
	```
	"full_path_to_python.exe" "%1" %*
	```
	
	![Registry Editor 1](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/2.png)
	
	Likely, previously, `%*` was missing. Similarly, set:
	```
	HKEY_CLASSES_ROOT\py_auto_file\shell\open\command
	```
	to the same value. 
	
	![Registry Editor 2](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/3.png)

- Now open a CLI window and run the command:
`where script_name`
If you see the full path to the script location on your file system, then you're ready to start using the scripts.

<a><Creating>
## Creating a new FX-Manager project
To start developing using FX-Manager, follow these steps:
- Create a new folder and name it with whatever you want. for example, `sample_fxm_proj`
- Open  CLI window and cd into the folder:
 `cd "full_path_to_sample_fxm_proj"`
- Run the following command to create the folder where the raw historical data will be placed:
`mkdir raw_data`
 - Now run the Command:
 `create_fx_proj --help`
you will see a full list of the arguments to pass depending on the what you want to do, for now, we will be creating a simple project to **back-test** a simple trading strategy with historical data consisting of **3 days** of type '**period_candles**' on a user defined portfolio (no portfolo construction is used) consisting of the **7-major currency pairs** ,  run the following command:
	```
	create_fx_proj -at back_tester -rdd raw_data -rdt period_candles -fnf "cccccc yyyy mm dd               " -nd 3 -ncp 7 -ntf 10
	```
	this creates the files and folder shown below:

	![Root Directory](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/4.png)

	![Data Directory](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/5.png)

- Download the sample dataset from [here](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/sample_data/) and copy the CSV files into the `raw_data` folder.
 See [Data collection](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/data_collection.md) tutorial to find out more about supported data types and formats.

- Now we need to pre-process the data before running the simulation, in order to do so, we need to configure the `raw_data_formats.json` file which contains information about column names in the raw data files as shown:

	![Raw Data Formats](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/6.png)

	for now, we shall use the default values, but if you use different dataset, make sure to modify it depending on the data type you passed with `create_fx_proj` in the `-rdt` argument.
- Now run the command to pre-process the data:
	```
	fx_pp.py -at back_tester -rdt period_candles
	```
	this reformats and copies the raw data from `raw_data` folder into the `data\raw_data\` directory.

- Now that data pre-processing is done, we need to define the trading strategy to be tested in the `strategy.py` file, since the topic of building algorithmic trading strategies is not crucial here, we will use the sample code provided [here](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/sample_strategy.py), copy and paste the code in it's specified place in the `strategy.py` file as shown:

	![Trading Strategy](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/7.png)
	
- Now all what's left is to modify the `kwargs_template` and `get_portfolios_template` functions as shown below to pass the required trading strategy arguments and the portfolio to be used for simulation.

	![Required arguments for the trading strategy](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/8.png)

	![Currency Pairs Portfolio](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/9.png)
	
- That's it! now we're all setup and ready to run the back test using the command:
	```
	run_fx_hist_sim -lvrg "0.01" -nd 3 -usp -uds
	```
	while the test is running you will see the daily results of the test as shown:

	![Daily results](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/10.png)
	
- After the test finishes, you will find 3 CSV Files in the `data\stats\historical_simulation_orders\` directory, each file contains the history of all the trades made in each day from the dataset as shown:
	![Daily Orders Files](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/11.png)

	![Daily Orders](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/assets/getting_started/12.png)

## Next Steps
For a detailed tutorial on back testing trading strategies see the [Running historical trading simulation](https://github.com/AbdullahBahi/fx-manager/tree/main/tutorials/hist_sim.md) tutorial.
Also, make sure to check the other tutorials listed [here](https://fx-manager.readthedocs.io/en/latest/tutorials.html) for other applications of FX-Manager.

If you have any suggested edits or need to contact me for any reason, feel free to do so on any of my social channels listed [here](https://fx-manager.readthedocs.io/en/latest/about_author.html).
