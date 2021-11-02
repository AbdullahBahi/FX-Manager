# FX-Manager
FX-Manager is a python package for developing and testing forex algorithmic trading strategies.

## Contents
- [**Features**](#Features)  
- [**Installation**](#Installation)  
- [**Documentation**](#Documentation)  
- [**Tutorials**](#Tutorials)  
- [**License**](#License)  
- [**About Author**](#Author)  

# Features
1. ### Historical market data collection and pre-processing
    - with FX-Manager, you can easily collect historical data from MT4 history center and preprocess it in just a few lines of code.

2. ### Flexibility with historical data formats
    - whether the data is OHLCV or bid-ask, whether it's daily or over a period of time, all what it takes is a simple configuration and the data will be ready to be used in FX-Managers applications.

3. ### Open virtual trading account with no limitations
    - most forex and stock brokers offer virtual trading accounts for new traders to learn trading with no risk of losing money. this might be sufficient for manual trading, but when it comes to algorithmic trading, it's not practical to use broker's virtual accounts to test trading strategies due to their limitations in terms of balance and time it takes to open a new account when an account is exhausted.  
    
    - with FX-Manager, there is no need to be constrained with broker's limitations, instead of performing actual trading in your broker's account each time a trading strategy ia tested, FX-Manager creates an instance of a virtual account with all properties as an actual account and performs trading simulation on this instance without affecting the actual account on MT4 trading platform.  
    
    - user can initialize this instance with any amount of balance and any account type with no limitations.

4. ### Run real-time trading simulation using real market prices
    - using FX-Manager's virtual accounts, you can test your user-defined trading strategy by runinig real-time trading simulation with real market prices from MT4 live price feed.
    
    - this allows you to run multiple simulations in the same time because each simulation uses it's own account instance without affecting the account connected with MT4. MT4 only acts as a price feed source for all running instances.
    
    - the simulation shows account state every time period that is defined by user.
5. ### Run historical trading simulation using historical market prices
    - in addition to real-time testing, you can also test your trading strategies using historical data and preview results in a very nice and well-stractured manner.

6. ### Biult-in portfolio construction and optimization
    - what currency pairs to invest in and what time frame should be used for each currency pair are both the most important questions for any forex trader.
    
    - with FX-Manager portfolio construction feature. you can construct optimized portfolios consisting of diversified collection of currency pairs in the best time frame for each pair. these portfolios are constructed with historical data and can be used for historical and live trading simulations.

## Installation
Fx-Manager framework is mainly used to create client server applications where the client is the trading bot written in python using FX-Manager's APIs, and the server is an expert advisor that is installed on MT4 trading platform. To utilize the full capacity of the framework, the Following packages & softwares need to be installed and configured.

- **FX-Manager python framework**
- **MetaTrader4 (MT4) Trading Platform** 
- **Darwenix MQL4 Expert Advisor on MT4**  
 
In this step-by-step Guild, we'll install all the above requirments.
1. **Installing FX-Manager python framework.**
    - Using pip  
        `pip install fxmanager`
    - Using conda  
        `conda install fxmanager`
2. **Installing MetaTrader4 (MT4) Trading Platform.**
    > NOTE: If you already have installed MT4 software and registered an active trading account, feel free to skip to next step.

    In order to use MT4 trading platform, you need to create virtual or actual trading account with a broker that supports the platform. then log in with the account on MT4 platform.  
    There are many broker's available that support MT4, for this guild we will use a demo acoount offered by [XM](https://www.xm.com/). 
    Follow the steps in this [Youtube Tutorial](https://youtu.be/QXiEalMebh0) by [The Forex Tutor](https://www.youtube.com/channel/UCBlO0JjC1xNVPOtCFTpEeWw) to create a demo account on [XM](https://www.xm.com/), download and install MT4 platform and finally log in with the account on the platform.

3. **Installing Darwenix MQL4 Expert Advisor on MT4.**  
    FX-Manager uses [Darwinex ZeroMQ Connector](https://www.darwinex.com/algorithmic-trading/zeromq-metatrader) to connect python clients to MetaTrader. So we need to install and configure Darwinex's [Expert Advisor](https://www.metatrader4.com/en/trading-platform/help/autotrading/experts) on MT4 platform.
    Follow the steps in this [Youtube Tutorial](https://www.youtube.com/watch?v=N0-aYLllK3E&list=PLv-cA-4O3y97vTpghgRqiPBjmpgWskYDl&index=4) by [Darwinex's Official channel](https://www.youtube.com/channel/UCBlO0JjC1xNVPOtCFTpEeWw) to install and configure the EA. 
    > NOTE: Skip the part from 1:30 to 4:10 in the tutorial.

Now you are all setup to start developing algorithmic trading strategies in python using FX-Manager. Refer to [**Tutorials**](#Tutorials) Section to get started.

## Documentation


## Tutorials
1. [Step-by-step installation guild.](#Installation)
2. Data collection 
3. Setting up new projects 
4. Data pre-processing 
5. Running portfolio optimization test on historical data
6. Running historical trading simulation
7. Running real-time trading simulaton

## About Author


## License 

