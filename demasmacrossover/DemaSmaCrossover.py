# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import numpy as np

# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class DemaSmaCrossover(IStrategy):
    stoploss = -0.25
    timeframe = "4h"

    minimal_roi = {
        "240": 0.05,
        "480": 0.1,
        "720": 0.17,
        "960": 0.22,
        "0": 0.3,
    }

    plot_config = {
        "main_plot": {
            # Configuration for main plot indicators.
            # Specifies `ema10` to be red, and `ema50` to be a shade of gray
            "dema": {"color": "red"},
            "sma": {"color": "blue"},
        },
        "subplots": {
            # Additional subplot RSI
            "rsi": {"rsi": {"color": "blue"}, "rsi_sma": {"color": "red"}},
        },
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["lt_sma"] = ta.SMA(dataframe, timeperiod=55)
        dataframe["sma"] = ta.SMA(dataframe, timeperiod=21)
        dataframe["dema"] = ta.DEMA(dataframe, timeperiod=9)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["rsi_sma"] = dataframe["rsi"].rolling(window=21).mean()

        # SMA check
        dataframe["ma_pos"] = np.where(dataframe["dema"] > dataframe["sma"], 1, 0)
        # RSI check
        dataframe["rsi_pos"] = np.where(dataframe["rsi"] > dataframe["rsi_sma"], 1, 0)
        # Posities tellen
        dataframe["pos_cnt"] = dataframe["ma_pos"] + dataframe["rsi_pos"]
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["close"]>dataframe["lt_sma"])
                & (dataframe["pos_cnt"] == 2)
            ),
            "buy",
        ] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["dema"] < dataframe["sma"])
            ),
            "sell",
        ] = 1
        return dataframe
