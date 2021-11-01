#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This Module is used as an API to get historic data from the MT4 EA.

This is a modified version of an example of using the Darwinex ZeroMQ Connector for Python 3 and MetaTrader 4 PULL REQUEST for v2.0.1 in which a Client requests rate history from a Daily from a start date to an end date. The user creates a 'rates_historic' object and using the methods 'get_daily_candles' and 'get_period_candles' the user client can get the historic data of the desired symbols. 

The original example is referenced [here](https://github.com/darwinex/dwx-zeromq-connector/blob/master/v2.0.1/python/examples/template/strategies/rates_historic.py).

Through commmand HIST, this client can select multiple rates from an INSTRUMENT (symbol, timeframe).
For example, to receive rates from instruments EURUSD(M1), between two dates, it will send this command to the Server, through its PUSH channel:

"HIST;EURUSD;1;2019.01.04 00:00:00;2019.01.14 00:00:00"
  
Original Author: [raulMrello](https://www.linkedin.com/in/raul-martin-19254530/)
Modified by    : [AbdullahBahi](https://www.linkedin.com/in/abdullahbahi/)  
"""

#############################################################################
# DWX-ZMQ required imports 
#############################################################################

# Import ZMQ-Strategy from relative path
from fxmanager.dwx.DWX_ZMQ_Strategy import DWX_ZMQ_Strategy

#############################################################################
# Other required imports
#############################################################################

import pandas as pd
from threading import Thread, Lock
from time import sleep
from os.path import join
import fxmanager._metadata as md
from __main__ import __dict__

__dict__.update(md.__dict__)

#############################################################################
# Class derived from DWZ_ZMQ_Strategy includes data processor for PULL,SUB data
#############################################################################

class rates_historic(DWX_ZMQ_Strategy):
    
    def __init__(self, 
                 _name="PRICES_SUBSCRIPTIONS",
                 _delay=0.1,
                 _broker_gmt=3,
                 _verbose=False):
        
        # call DWX_ZMQ_Strategy constructor and passes itself as data processor for handling
        # received data on PULL and SUB ports 
        super().__init__(_name,
                         [],          # Empty symbol list (not needed for this example)
                         _broker_gmt,
                         [self],      # Registers itself as handler of pull data via self.onPullData()
                         [self],      # Registers itself as handler of sub data via self.onSubData()
                         _verbose)
        
        # This strategy's variables
        self._delay = _delay
        self._verbose = _verbose
        self._finished = False

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
        # print('>> DWX MESSAGE >> Historic from ExpertAdvisor={}'.format(data))
        # _topic, _msg = data.split(" ")
        # print(_msg)
        pass
        
    ##########################################################################    
    def onSubData(self, data):        
        """
        Callback to process new data received through the SUB port
        """
        # split msg to get topic and message
        _topic, _msg = data.split(" ")
        # print('>> DWX MESSAGE >> Data on Topic={} with Message={}'.format(_topic, _msg))
        
    ##########################################################################    
    def get_daily_candles(self, save_to='', currency_pair='', date=''):        
        """
        Request historic data      
        """        
        self._finished = False
                
        # request rates
        print(f'>> DWX MESSAGE >> Requesting {currency_pair} Rates from {date}')
        self._zmq._DWX_MTX_SEND_HIST_REQUEST_(_symbol=currency_pair,
                                              _timeframe=1,
                                              _start=date + ' 00:00:00',
                                              _end=date + ' 23:59:00')
        while (currency_pair + '_M1') not in self._zmq._History_DB.keys():
          sleep(1)
        print('>> DWX MESSAGE >> Saving Data to CSV file ...\n')        
        df = pd.DataFrame(self._zmq._History_DB[currency_pair + '_M1'])
        df.to_csv(join(save_to, currency_pair + '_' + date + '.csv'))
        del df
        # finishes (removes all subscriptions)  
        self.stop()
  
    def get_period_candles(self, save_to='', currency_pair='', start='', end=''):        
        """
        Request historic data      
        """        
        self._finished = False
                
        # request rates
        print(f'>> DWX MESSAGE >> Requesting {currency_pair} Rates from {start} to {end}')
        self._zmq._DWX_MTX_SEND_HIST_REQUEST_(_symbol=currency_pair,
                                              _timeframe=1,
                                              _start=start + ' 00:00:00',
                                              _end=end + ' 23:59:00')
        while (currency_pair + '_M1') not in self._zmq._History_DB.keys():
          sleep(5)
        print('>> DWX MESSAGE >> Saving Data to CSV file ...\n')  
        df = pd.DataFrame(self._zmq._History_DB[currency_pair + '_M1'])
        df.to_csv(join(save_to, currency_pair + '_' + start + '_' + end + '.csv'))
        del df
        
        # finishes (removes all subscriptions)  
        self.stop()

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
        # print('>> DWX MESSAGE >> Unsubscribing from all topics')
          
      finally:
        # Release lock
        self._lock.release()
        sleep(self._delay)
      
      self._finished = True

""" -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
    SCRIPT SETUP
    -----------------------------------------------------------------------------------------------
    -----------------------------------------------------------------------------------------------
"""
if __name__ == "__main__":
  
  # Define timeframes
  timeframes = {'M1': 1,
                'M5': 5,
                'M15': 15,
                'M30': 30,
                'H1': 60,
                'H4': 240,
                'D1': 1440,
                'W1': 10080,
                'MN1': 43200
                }
  dates = {'M1': '2021.06.17 00:00:00',
          'M5': '2021.06.12 00:00:00',
          'M15': '2021.06.03 00:00:00',
          'M30': '2021.05.18 00:00:00',
          'H1': '2021.04.18 00:00:00',
          'H4': '2020.11.18 00:00:00',
          'D1': '2017.06.18 00:00:00',
          'W1': '2011.06.18 00:00:00',
          'MN1': '2001.06.18 00:00:00'
          }
  
  ## Recommended periods for different timeframes
  # > M1:  1 day       (2021.06.17 00:00:00 >> 2021.06.18 23:57:59)
  # > M5:  5 days      (2021.06.12 00:00:00 >> 2021.06.18 23:57:59)
  # > M15: 15 days     (2021.06.03 00:00:00 >> 2021.06.18 23:57:59)
  # > M30: 1 month     (2021.05.18 00:00:00 >> 2021.06.18 23:57:59)
  # > H1:  2 months    (2021.04.18 00:00:00 >> 2021.06.18 23:57:59)
  # > H4:  8 months    (2020.11.18 00:00:00 >> 2021.06.18 23:57:59)
  # > D1:  4 years     (2017.06.18 00:00:00 >> 2021.06.18 23:57:59)
  # > W1:  10 years    (2011.06.18 00:00:00 >> 2021.06.18 23:57:59)
  # > MN:  20 years    (2001.06.18 00:00:00 >> 2021.06.18 23:57:59)
  timeframe = 'M15'
  start = dates[timeframe]
  end = '2021.06.18 23:57:59'
  currency_pair = 'NZDUSD'
  
  # creates object with a predefined configuration: historic EURGBP_D1 between 4th adn 14th January 2019
  print('Loading example...')
  example = rates_historic()  

  # Starts example execution
  print('Running example...')

  example.run(currency_pair = currency_pair, timeframe = timeframes[timeframe], tf=timeframe, start=start, end=end)

  # Waits example termination
  print('Waiting example termination...')
  while not example.isFinished():
    sleep(1)
  print('Bye!!!')
  sleep(1)
