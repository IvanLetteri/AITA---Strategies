# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# --------------------------------
class bb_riding_strat(IStrategy):
    # Minimal ROI designed for the strategy.
    # adjust based on market conditions. We would recommend to keep it low for quick turn arounds
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "0": 0.3 #0.26   
    }

    # # Trailing stoploss
    # trailing_stop = True
    # trailing_only_offset_is_reached = True
    # trailing_stop_positive = 0.4
    # trailing_stop_positive_offset = 0.5


    # Optimal stoploss designed for the strategy
    stoploss = -0.235

    # Optimal timeframe for the strategy
    timeframe = '30m'

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Bollinger bands
        boll = ta.BBANDS(dataframe, nbdevup=2.0, nbdevdn=2.0, timeperiod=20)  #set timeperiod to your time period
        dataframe['bb_lower'] = boll['lowerband']
        dataframe['bb_middle'] = boll['middleband']
        dataframe['bb_upper'] = boll['upperband']
        # dataframe["bb_percent"] = (
        #     (dataframe["close"] - dataframe["bb_lower"]) /
        #     (dataframe["bb_upper"] - dataframe["bb_lower"])
        # )
        dataframe["bb_width"] = (
            (dataframe["bb_upper"] - dataframe["bb_lower"]) / dataframe["bb_middle"]
        )
        print(metadata)
        print(dataframe[["date","close","bb_upper","bb_middle","bb_lower","bb_width"]].tail(25))

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['close'] > dataframe['bb_upper']) 
                    # (dataframe['bb_width'] > 0.02) 
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    # (dataframe['adx'] < 25) &
            ),
            'sell'] = 1
        return dataframe

# /opt/freqtrade/.env/bin/freqtrade backtesting --config user_data/configs/backtest_conf.json --timerange=20171001-20210407 --strategy bb_riding_strat --timeframe=30m

#         Result for strategy bb_riding_strat
# ============================================================= BACKTESTING REPORT =============================================================
# |     Pair |   Buys |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |      Avg Duration |   Wins |   Draws |   Losses |
# |----------+--------+----------------+----------------+-------------------+----------------+-------------------+--------+---------+----------|
# | BTC/USDT |     35 |           9.63 |         337.19 |            67.505 |         112.40 | 29 days, 17:03:00 |     22 |       0 |       13 |
# | ETH/USDT |     45 |           8.52 |         383.44 |            76.765 |         127.81 | 18 days, 12:59:00 |     27 |       0 |       18 |
# | BNB/USDT |     48 |          12.61 |         605.23 |           121.168 |         201.74 |  21 days, 6:14:00 |     33 |       0 |       15 |
# | ADA/USDT |     17 |           0.33 |           5.54 |             1.110 |           1.85 |  21 days, 9:53:00 |      8 |       0 |        9 |
# | XRP/USDT |     18 |          -2.80 |         -50.39 |           -10.088 |         -16.80 |  26 days, 4:47:00 |      7 |       0 |       11 |
# |    TOTAL |    163 |           7.86 |        1281.02 |           256.460 |         427.01 | 22 days, 21:14:00 |     97 |       0 |       66 |
# ====================================================== SELL REASON STATS =======================================================
# |   Sell Reason |   Sells |   Wins |   Draws |   Losses |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |
# |---------------+---------+--------+---------+----------+----------------+----------------+-------------------+----------------|
# |           roi |      94 |     94 |       0 |        0 |          29.97 |        2817.18 |           564     |         939.06 |
# |     stop_loss |      66 |      0 |       0 |       66 |         -23.65 |       -1561.09 |          -312.53  |        -520.36 |
# |    force_sell |       3 |      3 |       0 |        0 |           8.31 |          24.92 |             4.989 |           8.31 |
# ========================================================== LEFT OPEN TRADES REPORT ===========================================================
# |     Pair |   Buys |   Avg Profit % |   Cum Profit % |   Tot Profit USDT |   Tot Profit % |      Avg Duration |   Wins |   Draws |   Losses |
# |----------+--------+----------------+----------------+-------------------+----------------+-------------------+--------+---------+----------|
# | BTC/USDT |      1 |          15.31 |          15.31 |             3.064 |           5.10 | 41 days, 22:00:00 |      1 |       0 |        0 |
# | BNB/USDT |      1 |           0.99 |           0.99 |             0.198 |           0.33 |          12:30:00 |      1 |       0 |        0 |
# | ADA/USDT |      1 |           8.63 |           8.63 |             1.728 |           2.88 | 32 days, 17:00:00 |      1 |       0 |        0 |
# |    TOTAL |      3 |           8.31 |          24.92 |             4.989 |           8.31 |  25 days, 1:10:00 |      3 |       0 |        0 |
# =============== SUMMARY METRICS ===============
# | Metric                | Value               |
# |-----------------------+---------------------|
# | Backtesting from      | 2017-10-01 00:00:00 |
# | Backtesting to        | 2021-04-07 00:00:00 |
# | Max open trades       | 3                   |
# |                       |                     |
# | Total trades          | 163                 |
# | Total Profit %        | 427.01%             |
# | Trades per day        | 0.13                |
# |                       |                     |
# | Best Pair             | BNB/USDT 605.23%    |
# | Worst Pair            | XRP/USDT -50.39%    |
# | Best trade            | BTC/USDT 29.97%     |
# | Worst trade           | BNB/USDT -23.65%    |
# | Best day              | 59.94%              |
# | Worst day             | -70.96%             |
# | Days win/draw/lose    | 89 / 1141 / 43      |
# | Avg. Duration Winners | 22 days, 9:55:00    |
# | Avg. Duration Loser   | 23 days, 13:53:00   |
# |                       |                     |
# | Abs Profit Min        | 6.000 USDT          |
# | Abs Profit Max        | 256.460 USDT        |
# | Max Drawdown          | 378.3%              |
# | Drawdown Start        | 2018-01-08 03:30:00 |
# | Drawdown End          | 2018-12-07 00:30:00 |
# | Market change         | 5145.39%            |
# ===============================================

