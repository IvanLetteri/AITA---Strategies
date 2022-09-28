# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

# --------------------------------
import talib.abstract as ta
import pandas_ta as pta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class HiLo(IStrategy):
    timeframe = "1d"
    stoploss = -100.0
    minimal_roi = {"0": 100.0}

# --- Plotting ---

    # Use this section if you want to plot the indicators on a chart after backtesting
    plot_config = {
        'main_plot': {
            # Create sma line
            'hilo': {'color': 'blue'},
        },
        'subplots': {
            # Create rsi subplot
            "MACD": {
                'macd': {'color': 'blue', 'fill_to': 'macdsignal'},
                'macdsignal': {'color': 'orange'},
                'macdhist': {'color': 'green', 'type': 'bar', 'plotly': {'opacity': 0.4}}
            },
        },
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Gann HiLo
        highl = 21
        lowl = 21
        dataframe["hilo"] = pta.hilo(
            high=dataframe["high"],
            low=dataframe["low"],
            close=dataframe["close"],
            high_length=highl,
            low_length=lowl,
            mamode=None,
            offset=None,
        )[f"HILO_{highl}_{lowl}"]

        # MACD
        macd = ta.MACD(
            dataframe,
            fastperiod=12,
            fastmatype=0,
            slowperiod=26,
            slowmatype=0,
            signalperiod=9,
            signalmatype=0,
        )
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]
        dataframe["macdhist"] = macd["macdhist"]

        # print(dataframe)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["close"] > dataframe["hilo"])
                & (dataframe["macdhist"] > 0)
            ),
            "buy",
        ] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # (dataframe["close"] < dataframe["hilo"])
                (dataframe["macdhist"] < 0)
            ),
            "sell",
        ] = 1
        return dataframe
