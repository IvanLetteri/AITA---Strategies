# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

# --- Custom libs here ---
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

# Class should have same name as file
class SmaRsiCrossover(IStrategy):
    # This strategy only uses crossover signals to enter/exit trades.
    timeframe = "1d"
    stoploss = -100.0
    minimal_roi = {"0": 100.0}

# --- Plotting ---

    # Use this section if you want to plot the indicators on a chart after backtesting
    plot_config = {
        'main_plot': {
            # Create sma line
            'sma': {'color': 'blue'},
        },
        'subplots': {
            # Create rsi subplot
            "rsi": {
                'rsi': {'color': 'orange'},
                'rsi_hline': {'color': 'grey','plotly': {'opacity': 0.4}}
            },
        },
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["sma"] = ta.SMA(dataframe, timeperiod=21)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["rsi_hline"] = 50
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
           (
               # Buy when close price crosses above sma if rsi > rsi_hline
               (
                   (dataframe['rsi'] > dataframe['rsi_hline'])
                   & (qtpylib.crossed_above(dataframe['close'], dataframe['sma']))
                   )
               # Else buy when rsi crosses above rsi_hline and close price > above sma 
               | (
                   (dataframe['close'] > dataframe['sma'])
                   & (qtpylib.crossed_above(dataframe['rsi'], dataframe['rsi_hline']))
                   )
           ),
           'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
           (
               # Sell when close price crosses below sma if rsi < rsi_hline
               (
                   (dataframe['rsi'] < dataframe['rsi_hline'])
                   & (qtpylib.crossed_below(dataframe['close'], dataframe['sma']))
                   )
               # Else sell when rsi crosses below rsi_hline and close price < above sma 
               | (
                   (dataframe['close'] < dataframe['sma'])
                   & (qtpylib.crossed_below(dataframe['rsi'], dataframe['rsi_hline']))
                   )
           ),
           'sell'] = 1

        return dataframe

