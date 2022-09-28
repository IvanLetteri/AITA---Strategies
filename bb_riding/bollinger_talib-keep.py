# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

rsi_lower = 25

class x_strat(IStrategy):
    stoploss = -0.2
    timeframe = "1d"

    order_types = {
        "buy": "limit",
        "sell": "limit",
        "emergencysell": "market",
        "stoploss": "market",
        "stoploss_on_exchange": True,
        "stoploss_on_exchange_interval": 60,
        "stoploss_on_exchange_limit_ratio": 0.99,
    }

    # minimal_roi = {
    #     "60": 0.6,
    #     "120": 0.05,
    #     "600": 0.035,
    #     "630": 0.012,
    #     "0": 0.09,
    # }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=7)
        dataframe["mfi"] = ta.MFI(dataframe, timeperiod=7)
        dataframe["sma"] = ta.SMA(dataframe, timeperiod=20) 


        boll = ta.BBANDS(dataframe, nbdevup=2.0, nbdevdn=2.0, timeperiod=20)  #set timeperiod to your time period
        dataframe['bb_lower'] = boll['lowerband']
        dataframe['bb_middle'] = boll['middleband']
        dataframe['bb_upper'] = boll['upperband']
        dataframe["bb_percent"] = (
            (dataframe["close"] - dataframe["bb_lower"]) /
            (dataframe["bb_upper"] - dataframe["bb_lower"])
        )
        # dataframe["bb_width"] = (
        #     (dataframe["bb_upper"] - dataframe["bb_lower"]) / dataframe["bb_middle"]
        # )
        print(metadata)
        print(dataframe.tail(50))
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # (dataframe["close"] > dataframe["EMA_QUICK"])
                # & (dataframe["EMA_QUICK"] > dataframe["EMA_SLOW"])
            ),
            "buy",
        ] = 1
        print((rsi_lower > dataframe["rsi"]).tail(50))
        # print((rsi_lower > dataframe["rsi"].shift(1)).tail(1))
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(), "sell",] = 1
        return dataframe
