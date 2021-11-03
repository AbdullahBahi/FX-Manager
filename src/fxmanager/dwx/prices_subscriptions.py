#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""    
This is a modified version of an example of using the Darwinex ZeroMQ Connector for Python 3 and MetaTrader 4 PULL REQUEST.

The original example is referenced `here <https://github.com/darwinex/dwx-zeromq-connector/blob/master/v2.0.1/python/examples/template/strategies/prices_subscriptions.py>`_, This Module is used as an API to get real time data from the MT4 EA. The user creates a 'prices_subscriptions' object with the desired symbols list in the client applicaction, then the real-time price feed can be accessed from the self._recent_prices dictionary.


Through commmand TRACK_PRICES, this client can select multiple SYMBOLS for price tracking.
For example, to receive real-time bid-ask prices from symbols EURUSD and GDAXI, this client will send this command to the Server, through its PUSH channel:

"TRACK_PRICES;EURUSD;GDAXI"

Server will answer through the PULL channel with a json response like this:

{'_action':'TRACK_PRICES', '_data': {'symbol_count':2}}

or if errors, then: 

{'_action':'TRACK_PRICES', '_data': {'_response':'NOT_AVAILABLE'}}

Once subscribed to this feed, it will receive through the SUB channel, prices in this format:

"EURUSD BID;ASK"
    
--
  
Original Author: `raulMrello <https://www.linkedin.com/in/raul-martin-19254530/>`_

Modified by    : `AbdullahBahi <https://www.linkedin.com/in/abdullahbahi/>`_
"""

#############################################################################
# DWX-ZMQ required imports 
#############################################################################

# Import ZMQ-Strategy from relative path
from fxmanager.dwx.DWX_ZMQ_Strategy import DWX_ZMQ_Strategy

#############################################################################
# Other required imports
#############################################################################

from threading import Thread, Lock
from time import sleep
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

#############################################################################
# Class derived from DWZ_ZMQ_Strategy includes data processor for PULL,SUB data
#############################################################################

class prices_subscriptions(DWX_ZMQ_Strategy):
    
    def __init__(self, 
                 _name="PRICES_SUBSCRIPTIONS",
                 _symbols=['EURUSD','GDAXI'],
                 _delay=0.1,
                 _broker_gmt=3,
                 _verbose=False):
        
        # call DWX_ZMQ_Strategy constructor and passes itself as data processor for handling
        # received data on PULL and SUB ports 
        super().__init__(_name,
                         _symbols,
                         _broker_gmt,
                         [self],      # Registers itself as handler of pull data via self.onPullData()
                         [self],      # Registers itself as handler of sub data via self.onSubData()
                         _verbose)
        
        # This strategy's variables
        self._symbols = _symbols
        self._delay = _delay
        self._verbose = _verbose
        self._finished = False
        self._data_available = False
        self._recent_prices = {'AUDUSD':0, 'EURUSD':0, 'GBPUSD':0, 'NZDUSD':0, 'USDCAD':0, 'USDCHF':0,
                               'USDCHN':0, 'USDDKK':0, 'USDHKD':0, 'USDHUF':0, 'USDJPY':0, 'USDMXN':0,
                               'USDNOK':0, 'USDPLN':0, 'USDSEK':0, 'USDSGD':0, 'USDZAR':0, 'BTCUSD':0,
                               'USDCZK':0, 'USDTRY':0, 'EURAUD':0, 'EURCAD':0, 'EURCHF':0, 'EURCZK':0,
                               'EURDKK':0, 'EURGBP':0, 'EURHKD':0, 'EURHUF':0, 'EURJPY':0, 'EURMXN':0,
                               'EURNOK':0, 'EURNZD':0, 'EURPLN':0, 'EURSEK':0, 'EURSGD':0, 'EURTRY':0,
                               'EURZAR':0}

        # lock for acquire/release of ZeroMQ connector
        self._lock = Lock()
        
    ##########################################################################    
    def isFinished(self):        
        """ Check if execution finished"""
        return self._finished
        
    ##########################################################################    
    def onPullData(self, data):        
        """
        Callback to process new data received through the PULL port
        """        
        # print responses to request commands
        print('>> DWX MESSAGE >> Response from ExpertAdvisor={}'.format(data))
        
    ##########################################################################    
    def onSubData(self, data):        
        """
        Callback to process new data received through the SUB port
        """
        self._data_available = True
        # split msg to get topic and message
        _topic, _msg = data.split(" ")
        self._recent_prices[_topic] = [float(i) for i in _msg.strip().split(';')]

    ##########################################################################    
    def run(self):        
        """
        Starts price subscriptions
        """        
        self._finished = False

        # Subscribe to all symbols in self._symbols to receive bid,ask prices
        self.__subscribe_to_price_feeds()

    ##########################################################################    
    def stop(self):
      """
      unsubscribe from all market symbols and exits
      """
        
      # remove subscriptions and stop symbols price feeding
      try:
        # Acquire lock
        self._lock.acquire()
        self._zmq._DWX_MTX_UNSUBSCRIBE_ALL_MARKETDATA_REQUESTS_()
        print('>> DWX MESSAGE >> Unsubscribing from all topics')
          
      finally:
        # Release lock
        self._lock.release()
        sleep(self._delay)
      
      try:
        # Acquire lock
        self._lock.acquire()
        self._zmq._DWX_MTX_SEND_TRACKPRICES_REQUEST_([])        
        print('>> DWX MESSAGE >> Removing symbols list')
        sleep(self._delay)
        self._zmq._DWX_MTX_SEND_TRACKRATES_REQUEST_([])
        print('>> DWX MESSAGE >> Removing instruments list')

      finally:
        # Release lock
        self._lock.release()
        sleep(self._delay)

      self._finished = True


    ##########################################################################
    def __subscribe_to_price_feeds(self):
      """
      Starts the subscription to the self._symbols list setup during construction.
      1) Setup symbols in Expert Advisor through self._zmq._DWX_MTX_SUBSCRIBE_MARKETDATA_
      2) Starts price feeding through self._zmq._DWX_MTX_SEND_TRACKPRICES_REQUEST_
      """
      if len(self._symbols) > 0:
        # subscribe to all symbols price feeds
        for _symbol in self._symbols:
          try:
            # Acquire lock
            self._lock.acquire()
            self._zmq._DWX_MTX_SUBSCRIBE_MARKETDATA_(_symbol)
            print('>> DWX MESSAGE >> Subscribed to {} price feed'.format(_symbol))
              
          finally:
            # Release lock
            self._lock.release()        
            sleep(self._delay)

        # configure symbols to receive price feeds        
        try:
          # Acquire lock
          self._lock.acquire()
          self._zmq._DWX_MTX_SEND_TRACKPRICES_REQUEST_(self._symbols)
          print('>> DWX MESSAGE >> Configuring price feed for {} symbols'.format(len(self._symbols)))
            
        finally:
          # Release lock
          self._lock.release()
          sleep(self._delay)      


""" -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
    SCRIPT SETUP
    -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
"""
if __name__ == "__main__":
  import DWX_ZMQ_Strategy
  # creates object with a predefined configuration: symbol list including EURUSD and GDAXI
  print('Loading example...')
  example = prices_subscriptions(_symbols=['EURUSD','USDCAD'])  

  # Starts example execution
  print('running example...')  
  example.run()

  while not price_feed.isFinished():
        feed = price_feed.get_prices()
        if feed is None:
            break
        currency_pair = feed[0]
        prices = feed[1]
        print(f'Pair: {feed[0]}    Price: {feed[1]}')
        sleep(1)
