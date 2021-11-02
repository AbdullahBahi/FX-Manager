"""
FX-Manager is a python package for developing and testing forex algorithmic trading strategies.

Main Features:
  1. historical data collection and pre-processing: 
      - with FX-Manager, you can easily collect historical data from MT4 history center and preprocess it in just a few lines of code.

  2. flexibility with historical data formats:
      - whether the data is OHLCV or bid-ask, whether it's daily or over a period of time, all what it takes is a simple configuration and the data will be ready to be used in FX-Managers applications.

  3. open virtual trading account with no limitations:
      - most forex and stock brokers offer virtual trading accounts for new traders to learn trading with no risk of losing money. this might be sufficient for manual trading, but when it comes to algorithmic trading, it's not practical to use broker's virtual accounts to test trading strategies due to their limitations in terms of balance and time it takes to open a new account when an account is exhausted.
      - with FX-Manager, there is no need to be constrained with broker's limitations, instead of performing actual trading in your broker's account each time a trading strategy ia tested, FX-Manager creates an instance of a virtual account with all properties as an actual account and performs trading simulation on this instance without affecting the actual account on MT4 trading platform.
      - user can initialize this instance with any amount of balance and any account type with no limitations.

  4. run real-time trading simulation using real market prices:
      - using FX-Manager's virtual accounts, you can test your user-defined trading strategy by runinig real-time trading simulation with real market prices from MT4 live price feed.
      - this allows you to run multiple simulations in the same time because each simulation uses it's own account instance without affecting the account connected with MT4. MT4 only acts as a price feed source for all running instances.
      - the simulation shows account state every time period that is defined by user.

  5. run historical trading simulation using historical market prices:
      - in addition to real-time testing, you can also test your trading strategies using historical data and preview results in a very nice and well-stractured manner.

  6. biult-in portfolio construction and optimization:
      - what currency pairs to invest in and what time frame should be used for each currency pair are both the most important questions for any forex trader.
      - with FX-Manager portfolio construction feature. you can construct optimized portfolios consisting of diversified collection of currency pairs in the best time frame for each pair. these portfolios are constructed with historical data and can be used for historical and live trading simulations.

Sub-Packages:
  1. basic        : contains mudules of helper functions used intrnally in all FX-Manager's sub-packages and functions used for setting up new FX-Manager projects and preprocessing data.
  2. dwx          : contains a modified version of Darwinex ZeroMQ connector which is used for connecting client code to MT4 trading platform.
  3. optimization : contains the mudules used for portfolio construction and optimization.
  4. simulation   : contains the modules used for historical and live trading sumulations.
  5. strategies   : contains the mudules used for building and injecting trading strategies int FX-Manager's trading simulations.
"""

from . import basic
from . import dwx
from . import optimization
from . import simulation
from . import strategies
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)