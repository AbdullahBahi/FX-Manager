Installation
============

Fx-Manager framework is mainly used to create client server applications where the client is the trading bot written in python using FX-Manager's APIs, and the server is an expert advisor that is installed on MT4 trading platform. To utilize the full capacity of the framework, the Following packages & softwares need to be installed and configured.

- **FX-Manager python framework**
- **MetaTrader4 (MT4) Trading Platform** 
- **Darwenix MQL4 Expert Advisor on MT4**  
 
In this step-by-step Guild, we'll install all the above requirments.

1. **Installing FX-Manager python framework.**
    - Using pip  
        `pip install FX-Manager`

2. **Installing MetaTrader4 (MT4) Trading Platform.**

    > **NOTE**: If you already have installed MT4 software and registered an active trading account, feel free to skip to next step.

    In order to use MT4 trading platform, you need to create virtual or actual trading account with a broker that supports the platform. then log in with the account on MT4 platform.  
    There are many broker's available that support MT4, for this guild we will use a demo acoount offered by `XM.COM <https://www.xm.com/>`_. 

    Follow the steps in this `Youtube Tutorial1 <https://youtu.be/QXiEalMebh0>`_ by `The Forex Tutor <https://www.youtube.com/channel/UCBlO0JjC1xNVPOtCFTpEeWw>`_ to create a demo account on `XM.COM <https://www.xm.com/>`_, download and install MT4 platform and finally log in with the account on the platform.

3. **Installing Darwenix MQL4 Expert Advisor on MT4.**  

    FX-Manager uses `Darwinex ZeroMQ Connector <https://www.darwinex.com/algorithmic-trading/zeromq-metatrader>`_ to connect python clients to MetaTrader. So we need to install and configure Darwinex's `Expert Advisor <https://www.metatrader4.com/en/trading-platform/help/autotrading/experts>`_ on MT4 platform.

    Follow the steps in this `Youtube Tutorial2 <https://www.youtube.com/watch?v=N0-aYLllK3E&list=PLv-cA-4O3y97vTpghgRqiPBjmpgWskYDl&index=4>`_ by `Darwinex's Official channel <https://www.youtube.com/channel/UCBlO0JjC1xNVPOtCFTpEeWw>`_ to install and configure the EA.

    > **NOTE**: Skip the part from 1:30 to 4:10 in the tutorial.

Now you are all setup to start developing algorithmic trading strategies in python using FX-Manager. Refer to **Tutorials** Section to get started.