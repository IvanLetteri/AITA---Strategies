# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from functools import reduce
from pandas import DataFrame

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,IStrategy, IntParameter)

# --- Add your lib to import here ---
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

# --- Generic strategy settings ---

class SmaCrossover(IStrategy):
    INTERFACE_VERSION = 2
    
    # Determine timeframe and # of candles before strategysignals becomes valid
    timeframe = '1d'
    
    # Determine roi take profit and stop loss points
    minimal_roi = {"0":  100.00}

    stoploss = -1
    trailing_stop = False
    use_sell_signal = True
    sell_profit_only = False
    sell_profit_offset = 0.0
    ignore_roi_if_buy_signal = False

# --- Plotting ---

    # Use this section if you want to plot the indicators on a chart after backtesting
    plot_config = {
        'main_plot': {
            # Create sma50 and sma200 line
            'quick_sma': {'color': 'blue'},
            'slow_sma': {'color': 'red'},
        },
        # 'subplots': {
        #     # Create subplot MACD
        #     "MACD": {
        #         'macd': {'color': 'blue', 'fill_to': 'macdsignal'},
        #         'macdsignal': {'color': 'orange'},
        #         'macdhist': {'color': 'green', 'type': 'bar', 'plotly': {'opacity': 0.4}}
        #     },
        # },
    }


# --- Define spaces for the indicators ---

    # Buy space - UNCOMMENT THIS FOR HYPEROPTING
    # quick_sma = IntParameter(35, 65, default=50, space="buy")
    # slow_sma = IntParameter(185, 215, default=200, space="buy")

# --- Used indicators of strategy code ----
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        # SMA's for buying - UNCOMMENT THIS FOR HYPEROPTING
        # for val in self.quick_sma.range:
        #     dataframe[f'quick_sma_{val}'] = ta.SMA(dataframe, timeperiod=val)
        # for val in self.slow_sma.range:
        #     dataframe[f'slow_sma_{val}'] = ta.SMA(dataframe, timeperiod=val)

        # Polulate SMA indicators - COMMENT THIS SECTION OUT WHEN HYPEROPTING
        dataframe['quick_sma'] = ta.SMA(dataframe, timeperiod=50)
        dataframe['slow_sma'] = ta.SMA(dataframe, timeperiod=200)

        return dataframe

# --- Buy settings ---
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
         # UNCOMMENT THIS FOR HYPEROPTING
    #    conditions = []
    #    conditions.append(qtpylib.crossed_above(
    #     dataframe[f'quick_sma_{self.quick_sma.value}'],
    #     dataframe[f'slow_sma_{self.slow_sma.value}']
    #     ))

    #    if conditions:
    #        dataframe.loc[
    #            reduce(lambda x, y: x & y, conditions),
    #            'buy'] = 1

    #    Enter the conditions for buying - COMMENT THIS SECTION OUT WHEN HYPEROPTING
       dataframe.loc[
           (
               # Buy when SMA 50 crosses above SMA 200
               (qtpylib.crossed_above(dataframe['quick_sma'], dataframe['slow_sma']))
           ),
           'buy'] = 1

       return dataframe

# --- long settings ---
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
       # UNCOMMENT THIS FOR HYPEROPTING
    #    conditions = []
    #    conditions.append(qtpylib.crossed_below(
    #     dataframe[f'quick_sma_{self.quick_sma.value}'],
    #     dataframe[f'slow_sma_{self.slow_sma.value}']
    #     ))

    #    if conditions:
    #        dataframe.loc[
    #            reduce(lambda x, y: x & y, conditions),
    #            'sell'] = 1
        
    #    Enter the conditions for selling - COMMENT THIS SECTION OUT WHEN HYPEROPTING
       dataframe.loc[
           (
               # Buy when SMA 50 crosses above SMA 200
               (qtpylib.crossed_below(dataframe['quick_sma'], dataframe['slow_sma']))
           ),
           'sell'] = 1

       return dataframe

