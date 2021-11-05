
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
        `pip install FX-Manager`
    
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
The full detailed documentation is provided [here](https://fx-manager.readthedocs.io/en/latest/modules.html).


## Tutorials
1. [Getting started](https://github.com/AbdullahBahi/fx-manager/blob/main/tutorials/getting_started.md)
2. [Data collection](https://github.com/AbdullahBahi/fx-manager/blob/main/tutorials/data_collection.md) 
3. [Setting up new projects](https://github.com/AbdullahBahi/fx-manager/blob/main/tutorials/creating_new_projs.md)
4. [Data pre-processing](https://github.com/AbdullahBahi/fx-manager/blob/main/tutorials/preprocessing.md)
5. [Running portfolio optimization test on historical data](https://github.com/AbdullahBahi/fx-manager/blob/main/tutorials/optim.md)
6. [Running historical trading simulation](https://github.com/AbdullahBahi/fx-manager/blob/main/tutorials/hist_sim.md)
7. [Running real-time trading simulaton](https://github.com/AbdullahBahi/fx-manager/blob/main/tutorials/live_sim.md)

## About Author
This project is built and maintained by Abdullah Bahi, Junior data analyst with a robust background in machine and deep learning. Also, a professional python developer with wide knowledge and hands-on experience with most of the packages used in AI and Data Science.

##### Skills & Experience

- **Certifications** : AWS Certified Data Analytics Specialist

- **Expertise Areas** :

    - Data Analysis
    - Data Visualization
    - ETL
    - Data Base (SQL)
    - Machine Learning
    - Deep Learning
    - Amazon Web Services (AWS)
    - Open Source Software Development (OSS)
    - Business Analysis
    - Financial Data Analysis

- **Technologoes & Tools** :

    - Python 3.x
    - IPython Notebooks
    - Power BI
    - SSIS
    - Linux
    - Anaconda
    - Microsoft Office

##### General Information
- **Name** : Abdullah Bahi
- **Title** : Junior Data Analyst
- **Education** : Bachelors degree in Electronics and Communication Engineering (ECE)
- **Nationality** : Egypt

##### Social Channels & Contact Info
- [E-mail](abdullahbahi@icloud.com)
- [LinkedIn](https://www.linkedin.com/in/abdullahbahi/)
- [Twitter](https://twitter.com/abdullahbahi_)
- [Youtube Channel](https://www.youtube.com/channel/UC9WE0svD0DJarkMvzOnRWlw)

## License 
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

 [Copyright (C) 2007 Free Software Foundation, Inc](https://fsf.org/)
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.
 
#### Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.

