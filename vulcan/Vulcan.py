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

class vulcan(IStrategy):
    stoploss = -0.25
    timeframe = "30m"
    minimal_roi = {"0":  100}

    plot_config = {
        "main_plot": {
            "SMA": {"color": "red"},
        },
        "subplots": {
            "STOCH": {
                "slowd": {"color": "blue"},
                "slowk": {"color": "orange"},
            },
            "RSI": {
                "RSI": {"color": "blue"},
                "RSI_SMA": {"color": "orange"},
            },
        },
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["RSI"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["RSI_SMA"] = dataframe["RSI"].rolling(window=50).mean()

        dataframe["SMA"] = ta.SMA(dataframe, timeperiod=23)
        dataframe["growing_SMA"] = (
            (dataframe["SMA"] > dataframe["SMA"].shift(1))
            & (dataframe["SMA"].shift(1) > dataframe["SMA"].shift(2))
            & (dataframe["SMA"].shift(2) > dataframe["SMA"].shift(3))
        )

        stoch = ta.STOCH(
            dataframe,
            fastk_period=14,
            slowk_period=4,
            slowk_matype=0,
            slowd_period=6,
            slowd_matype=0,
        )
        dataframe["slowd"] = stoch["slowd"]
        dataframe["slowk"] = stoch["slowk"]

        dataframe["stoch_sell_cross"] = ((dataframe["slowd"] > 75) & (dataframe["slowk"] > 75)) & (qtpylib.crossed_below(dataframe["slowk"], dataframe["slowd"]))

        dataframe["last_lowest"] = dataframe["low"].rolling(100).min().shift(1)
        dataframe["lower_low"] = dataframe["close"] < dataframe["last_lowest"]

        # Print stuff
        # print(dataframe[['date','close','low','last_lowest','lower_low']].loc[dataframe['lower_low'] == True].tail(55))
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["close"] > dataframe["SMA"])
                & (dataframe["growing_SMA"])
                & (dataframe["RSI"] > dataframe["RSI_SMA"])
                & (dataframe["RSI"] > 50)
            ),
            "buy",
        ] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            ((dataframe["stoch_sell_cross"] == True) | (dataframe["lower_low"] == True)),
            "sell",
        ] = 1
        return dataframe

