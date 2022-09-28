# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

# --------------------------------
import talib.abstract as ta
import pandas_ta as pta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class hilo_strat(IStrategy):
    minimal_roi = {"0": 100.0}
    stoploss = -100.0
    timeframe = "4h"

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Gann HiLo
        dataframe["hilo"] = pta.hilo(
            high=dataframe["high"],
            low=dataframe["low"],
            close=dataframe["close"],
            high_length=21,
            low_length=21,
            mamode=None,
            offset=None,
            )["HILO_21_21"]
        # dataframe["buy1"] = dataframe["close"] > dataframe["hilo"]

        # MACD Histogram
        dataframe["macdh"] = pta.macd(
            close=dataframe["close"],
            fast=29,
            slow=30,
            signal=None,
            offset=None
            )["MACDh_29_30_9"]
        # dataframe["buy2"] = dataframe["macdh"] > 0

        # ===== UITSTAP INDICATOREN =====
        # Slow stochastic
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

        # dataframe["stoch_sell_cross"] = ((dataframe["slowd"] > 75) & (dataframe["slowk"] > 75)) & (
        #     qtpylib.crossed_above(dataframe["slowd"], dataframe["slowk"])
        # )

        # Closeprice below lower low last 100 candles
        dataframe["last_lowest"] = dataframe["low"].rolling(100).min().shift(1)
        dataframe["lower_low"] = dataframe["close"] < dataframe["last_lowest"]
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            # ((dataframe["buy1"] == True) & (dataframe["buy2"] == True)),
            ((dataframe["close"] > dataframe["hilo"]) 
            & (dataframe["macdh"] > 0)),
            "buy",
        ] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # (dataframe["stoch_sell_cross"] == True)
                ((dataframe["slowd"] > 75) & (dataframe["slowk"] > 75)) 
                & (qtpylib.crossed_above(dataframe["slowd"], dataframe["slowk"]))
            ),
            "sell",
        ] = 1
        return dataframe
