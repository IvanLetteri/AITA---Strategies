# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

# --------------------------------
import talib.abstract as ta
import pandas_ta as pta
import freqtrade.vendor.qtpylib.indicators as qtpylib

# ---------- Commands -----------
# Commands for backtesting etc.:
# /opt/freqtrade/.env/bin/freqtrade backtesting --config user_data/configs/backtest_conf.json --strategy tripple_supertrend
# /opt/freqtrade/.env/bin/freqtrade backtesting --config user_data/configs/backtest_conf.json --timerange=20210201-20210310 --strategy tripple_supertrend --export trades --export-filename=user_data/backtest_results/simple_strat_30m_test.json
# /opt/freqtrade/.env/bin/freqtrade plot-dataframe --config user_data/configs/backtest_conf.json --strategy tripple_supertrend  --export-filename=user_data/backtest_results/tripple_supertrend-2021-05-13_19-29-25.json
# /opt/freqtrade/.env/bin/freqtrade plot-profit --config user_data/configs/backtest_conf.json  --strategy tripple_supertrend --export-filename=user_data/backtest_results/tripple_supertrend-2021-05-13_19-29-25.json
# --------------------------------


class tripple_supertrend_1d(IStrategy):
    stoploss = -1
    timeframe = "1d"

    order_types = {
        "buy": "limit",
        "sell": "limit",
        "emergencysell": "market",
        "stoploss": "market",
        "stoploss_on_exchange": False,
        "stoploss_on_exchange_interval": 60,
        "stoploss_on_exchange_limit_ratio": 0.99,
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Indicatoren
        dataframe["st_ultra_d"] = pta.supertrend(
            high=dataframe["high"],
            low=dataframe["low"],
            close=dataframe["close"],
            length=10,
            multiplier=3,
        )["SUPERTd_10_3.0"]
        dataframe["st_long_d"] = pta.supertrend(
            high=dataframe["high"],
            low=dataframe["low"],
            close=dataframe["close"],
            length=10,
            multiplier=1.8,
        )["SUPERTd_10_1.8"]
        dataframe["st_medium_d"] = pta.supertrend(
            high=dataframe["high"],
            low=dataframe["low"],
            close=dataframe["close"],
            length=10,
            multiplier=1.3,
        )["SUPERTd_10_1.3"]
        dataframe["st_short_d"] = pta.supertrend(
            high=dataframe["high"],
            low=dataframe["low"],
            close=dataframe["close"],
            length=10,
            multiplier=0.8,
        )["SUPERTd_10_0.8"]

        # Trade R:R bepalen
        def get_position(row):
            if (
                row["st_ultra_d"] == 1
                and row["st_long_d"] == 1
                and row["st_medium_d"] == 1
                and row["st_short_d"] == 1
            ):
                val = "high_r_long"  # R:R 1:5 long position
            elif (
                row["st_ultra_d"] == -1
                and row["st_long_d"] == 1
                and row["st_medium_d"] == 1
                and row["st_short_d"] == 1
            ):
                val = "low_r_long"  # R:R 1:2 long position
            else:
                val = "neutral"
            return val

        dataframe["position"] = dataframe.apply(get_position, axis=1)

        # Verandering advies detectie
        dataframe["advice_changed"] = dataframe["position"].shift(+1) != dataframe["position"]

        # Stoploss bepalen
        dataframe["stoploss"] = pta.supertrend(
            high=dataframe["high"],
            low=dataframe["low"],
            close=dataframe["close"],
            length=10,
            multiplier=1.8,
        )["SUPERT_10_1.8"]

        # Takeprofit
        tp_high = 1.5
        tp_low = 1.2
        for i, row in dataframe.iterrows():
            if row["position"] == "high_r_long" and row["advice_changed"] == True:
                dataframe.loc[i, "takeprofit"] = ((row["close"] - row["stoploss"]) * tp_high) + row[
                    "close"
                ]
            elif row["position"] == "low_r_long" and row["advice_changed"] == True:
                dataframe.loc[i, "takeprofit"] = ((row["close"] - row["stoploss"]) * tp_low) + row[
                    "close"
                ]
            else:
                dataframe.loc[i, "takeprofit"] = dataframe.loc[i - 1, "takeprofit"]

        # Print stuff
        # print(dataframe.tail(25))
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                ((dataframe["position"] == "high_r_long") | (dataframe["position"] == "low_r_long"))
                & (dataframe["advice_changed"] == True)
            ),
            "buy",
        ] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["close"] > dataframe["takeprofit"])
                | (dataframe["close"] < dataframe["stoploss"])
            ),
            "sell",
        ] = 1
        return dataframe
