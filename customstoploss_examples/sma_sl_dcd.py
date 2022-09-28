# Freqtrade default libraries (DO NOT REMOVE!).
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

# Additional libraries for dataframe, strategy and/or plotting.
# Remove any when not used.
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import pandas_ta as pta
import numpy as np  # noqa
import pandas as pd  # noqa

# These libs are for hyperopt, remove if not used.
from functools import reduce
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,IStrategy, IntParameter)

# Libs used for custom stoploss.
# For simplicity reasons I added all libraries, whether I use them or not. 
# Remove any when not used.
from datetime import datetime, timedelta
from freqtrade.persistence import Trade
from freqtrade.strategy import stoploss_from_absolute, stoploss_from_open
from freqtrade.exchange import timeframe_to_prev_date

class sma_sl_dcd(IStrategy):
    timeframe = "1d"
    # Both stoploss and roi are set to 100 to prevent them to give a sell signal.
    stoploss = -100
    minimal_roi = {"0": 100}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # sma
        dataframe['sma'] = ta.SMA(dataframe, timeperiod=50)

        # ATR for custom stoploss
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)

        # Create a custom takeprofit and stoploss level
        # Create signal condition (when closeprice is above sma)
        
        dataframe["entry"] = (dataframe['close'] > dataframe['sma'])
        # If previous entry is different than current entry, then there is a change in conditions
        dataframe["buy_signal"] = (dataframe["entry_1"].shift(+1) != dataframe["entry_1"])&(dataframe["entry_1"] == True)
        
        
        for i, row in dataframe.iterrows():
            if row['buy_signal'] == True:
                dataframe.loc[i,'tp'] = ((row['close']-row['sl']) * row['sl_fact']) + row['close']
        else:
            dataframe.loc[i,'tp'] = dataframe.fillna(method='ffill', inplace=True)
        

        # Print stuff for debugging dataframe
        print(dataframe[dataframe["signal"]==True].tail(20))
        # print(dataframe.tail(55))
        return dataframe
    

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            # (qtpylib.crossed_above(dataframe['close'], dataframe['sma'])),
            (dataframe['close'] > dataframe['sma']),
             ['buy', 'buy_tag']] = (1, 'buy_signal_sma_cross')

        return dataframe


    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (qtpylib.crossed_below(dataframe['close'], dataframe['sma'])),
            "sell",
            ] = 1
        return dataframe

