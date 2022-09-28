# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class Simple(IStrategy):
    """

    author@: Gert Wohlgemuth

    idea:
        this strategy is based on the book, 'The Simple Strategy' and can be found in detail here:

        https://www.amazon.com/Simple-Strategy-Powerful-Trading-Futures-ebook/dp/B00E66QPCG/ref=sr_1_1?ie=UTF8&qid=1525202675&sr=8-1&keywords=the+simple+strategy
    """

    # Minimal ROI designed for the strategy.
    # adjust based on market conditions. We would recommend to keep it low for quick turn arounds
    # This attribute will be overridden if the config file contains "minimal_roi"
    # DCD: Strategy apparently has a takeprofitpoint of 1%
    minimal_roi = {
        "0": 0.01
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    # DCD: strategy has 25% stoploss set after buy signal
    stoploss = -0.25

    # Optimal timeframe for the strategy
    # DCD: Original timeframe is 5 minute
    timeframe = '5m'

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # RSI
        # DCD: 7 period RSI configured for this strategy
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=7)

        # required for graphing
        # DCD: 12 period SMA bollinger band...
        bollinger = qtpylib.bollinger_bands(dataframe['close'], window=12, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_upperband'] = bollinger['upper']
        dataframe['bb_middleband'] = bollinger['mid']

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (
                    # Buy rules: If MACD is over 0 AND MACD is bigger than MACDSignal AND Bollinger upperband currend is bigger than
                    # Bollinger upperband previous period AND RSI is over 70
                    # Then BUY
                        (dataframe['macd'] > 0)  # over 0
                        & (dataframe['macd'] > dataframe['macdsignal'])  # over signal
                        & (dataframe['bb_upperband'] > dataframe['bb_upperband'].shift(1))  # pointed up
                        & (dataframe['rsi'] > 70)  # optional filter, need to investigate
                )
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # different strategy used for sell points, due to be able to duplicate it to 100%
        dataframe.loc[
            (
                # If RSI is greater than 80 then sell. Nothing more.
                (dataframe['rsi'] > 80)
            ),
            'sell'] = 1
        return dataframe
