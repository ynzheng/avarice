import ast
from configobj import ConfigObj
from threading import Lock

import avarice
import shelve

indicators_lock = Lock()
trader_lock = Lock()
simulator_lock = Lock()


class indicators:

  indshelve = ''

  def CreateShelveName():
    configurables = ['Short Period', 'Long Period', 'Period', 'Alpha Constant',
                     'Signal Period', 'Fast K Period', 'Full K Period',
                     'Full D Period', 'Tenkan-Sen Period', 'Senkou Span Period',
                     'Kijun-Sen Period', 'Chikou Span Period', 'Multiplier']
    configurable_values = []
    for indicator in ast.literal_eval(config.gc['Trader']['Trade Indicators']):
      if isinstance(indicator, list):
        for i in indicator:
          for c in configurables:
            try:
              configurable_values.append(config.gc['Indicators'][i][c])
            except KeyError:
              pass
      else:
        for c in configurables:
          try:
            configurable_values.append(config.gc['Indicators'][indicator][c])
          except KeyError:
            pass
    indicators.indshelve = config.gc['Database']['Path'] + '/' + \
        config.gc['API']['Trade Pair'] + config.gc['Candles']['Size'] + \
        ''.join(x for x in configurable_values) + 'indicators.shelve'

  def writelist(ln, key):
    if not key == None:
      indicators_lock.acquire()
      db = shelve.open(indicators.indshelve, writeback=True)
      if ln not in db:
        db[ln] = [key]
      else:
        temp = db[ln]
        temp.append(key)
        if ast.literal_eval(config.gc['Database']['Store All']):
          db[ln] = temp
        else:
          db[ln] = temp[-avarice.MaxCandleDepends:]
      db.close()
      indicators_lock.release()

  def getlist(ln):
    indicators_lock.acquire()
    db = shelve.open(indicators.indshelve, writeback=True)
    if ln not in db:
      temp = []
    else:
      try:
        temp = db[ln]
      except EOFError:
        try:
          temp = db[ln]
        except EOFError:
          temp = []
    db.close
    indicators_lock.release()
    return temp


class trades:

  def writelist(tradetype, ln, key):
    if not key == None:
      if tradetype == 'trader':
        tradelock = trader_lock
      else:
        tradelock = simulator_lock
      tradelock.acquire()
      db = shelve.open(
          config.gc['Database']['Path'] + '/' + tradetype + '.shelve')
      if ln not in db:
        db[ln] = [key]
      else:
        temp = db[ln]
        temp.append(key)
        if int(config.gc['Database']['Trade History Max']) == 0:
          db[ln] = temp
        else:
          db[ln] = temp[-int(config.gc['Database']['Trade History Max']):]
      db.close()
      tradelock.release()

  def getlist(tradetype, ln):
    if tradetype == 'trader':
      tradelock = trader_lock
    else:
      tradelock = simulator_lock
    tradelock.acquire()
    db = shelve.open(
        config.gc['Database']['Path'] + '/' + tradetype + '.shelve',
        writeback=True)
    if ln not in db:
      temp = []
    else:
      try:
        temp = db[ln]
      except EOFError:
        try:
          temp = db[ln]
        except EOFError:
          temp = []
    db.close
    tradelock.release()


class config:
  gc = {}

  def __init__(self):
    config.gc = ConfigObj("config.ini", list_values=False)
