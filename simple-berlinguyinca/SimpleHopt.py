# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import pandas_ta as pta
import numpy as np  # noqa
import pandas as pd  # noqa

# These libs are for hyperopt
from functools import reduce
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,IStrategy, IntParameter)
# --------------------------------
# freqtrade hyperopt --timeframe 1d --hyperopt-loss SharpeHyperOptLossDaily --space buy roi stoploss --epochs 10 -s SimpleHopt

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class SimpleHopt(IStrategy):
    """

    author@: Gert Wohlgemuth

    idea:
        this strategy is based on the book, 'The Simple Strategy' and can be found in detail here:

        https://www.amazon.com/Simple-Strategy-Powerful-Trading-Futures-ebook/dp/B00E66QPCG/ref=sr_1_1?ie=UTF8&qid=1525202675&sr=8-1&keywords=the+simple+strategy
    """

    minimal_roi = {"0": 0.01}
    stoploss = -0.25
    timeframe = '5m'

    # The hyperopt spaces where the optimal parameters for this strategy are hidden
    rsi_buy_hline = IntParameter(50, 75, default=70, space="buy")
    rsi_sell_hline = IntParameter(70, 95, default=80, space="sell")
    rsi_period = IntParameter(4, 16, default=7, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        macd = ta.MACD(
            dataframe,
            fastperiod=12,
            fastmatype=0,
            slowperiod=26,
            slowmatype=0,
            signalperiod=9,
            signalmatype=0,)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # For each value in the space of the indicator above, 
        # see if it produces better results in the buy/sell trend below
        for val in self.rsi_period.range:
            dataframe[f'rsi_{val}'] = ta.RSI(dataframe, timeperiod=val)

        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=12, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_upperband'] = bollinger['upper']
        dataframe['bb_middleband'] = bollinger['mid']

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (
                    # test the given indicator value in the buy condition
                        (dataframe['macd'] > 0)
                        & (dataframe['macd'] > dataframe['macdsignal'])
                        & (dataframe['bb_upperband'] > dataframe['bb_upperband'].shift(1))
                        & (dataframe[f'rsi_{self.rsi_period.value}'] > self.rsi_buy_hline.value)
                )
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # test the given indicator value in the sell condition
                (dataframe[f'rsi_{self.rsi_period.value}'] > self.rsi_sell_hline.value)
            ),
            'sell'] = 1
        return dataframe
