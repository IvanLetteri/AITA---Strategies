# Freqtrade default libraries (DO NOT REMOVE!).
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

# Additional libraries for dataframe, strategy and/or plotting.
# Remove any when not used.
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import pandas_ta as pta
import numpy as np  # noqa
import pandas as pd  # noqa

# These libs are for hyperopt, remove if not used.
from functools import reduce
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,IStrategy, IntParameter)

# Libs used for custom stoploss.
# For simplicity reasons I added all libraries, whether I use them or not. 
# Remove any when not used.
from datetime import datetime
from freqtrade.persistence import Trade
from freqtrade.strategy import stoploss_from_absolute, stoploss_from_open

class sma_sl_atr_fullcomment(IStrategy):
    timeframe = "1d"
    # Both stoploss and roi are set to 100 to prevent them to give a sell signal.
    stoploss = -100
    minimal_roi = {"0": 100}

    plot_config = {
        "main_plot": {
            "sma" : {"color": "blue"},
        },
        "subplots": {
            "atr": {
                "atr": {"color": "orange"},
            },
        },
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # sma
        dataframe['sma'] = ta.SMA(dataframe, timeperiod=50)

        # atr, used by the custom stoploss
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        
        # Print stuff for debugging dataframe
        # print(dataframe.tail(20))
        return dataframe
    
    
    # USE CUSTOM STOPLOSS
    use_custom_stoploss = True
    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Custom stoploss logic, returning the new distance relative to current_rate (as ratio).
        e.g. returning -0.05 would create a stoploss 5% below current_rate.
        The custom stoploss can never be below self.stoploss, which serves as a hard maximum loss.

        For full documentation please go to https://www.freqtrade.io/en/latest/strategy-advanced/

        When not implemented by a strategy, returns the initial stoploss value
        Only called when use_custom_stoploss is set to True.

        :param pair: Pair that's currently analyzed
        :param trade: trade object.
        :param current_time: datetime object, containing the current datetime
        :param current_rate: Rate, calculated based on pricing settings in ask_strategy.
        :param current_profit: Current profit (as ratio), calculated based on current_rate.
        :param **kwargs: Ensure to keep this here so updates to this won't break your strategy.
        :return float: New stoploss value, relative to the current rate
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        candle = dataframe.iloc[-1].squeeze()
        
        print(pair,trade,current_time,current_rate,current_profit,(current_rate - (candle['atr'] * 2)))
        print("\n Pair: ",pair,
            "\n Trade: ", trade,
            "\n Current time: ", current_time,
            "\n Current rate: ", current_rate,
            "\n Current profit: ", current_profit,
            "\n Trade open date UTC: ", trade.open_date_utc, 
            "\n Trade open rate: ", trade.open_rate, 
            "\n Trade open trade value: ", trade.open_trade_value,
            "\n Trade amount: ", trade.amount, 
            "\n Trade fee open: ", trade.fee_open, 
            "\n Trade initial stoploss: ", trade.initial_stop_loss, 
            "\n Trade initial stoploss percent: ", trade.initial_stop_loss_pct, 
            "\n Trade stoploss: ", trade.stop_loss, 
            "\n Trade stoposs percent: ", trade.stop_loss_pct, 
            "\n Trade ATR: ", (candle['atr']),
            "\n Trade ATR distance: ", (current_rate - (candle['atr'] * 2)),
            "\n Trade stake amount: ", trade.stake_amount, 
            "\n Trade total profit: ", trade.total_profit,
            "\n Trade exchange: ", trade.exchange,
            "\n Trade is open: ", trade.is_open,
            "\n Trade fee open currency: ", trade.fee_open_currency,
            "\n Trade amount requested: ", trade.amount_requested,
            "\n Trade use db: ", trade.use_db,
            "\n Trade strategy: ", trade.strategy,
            "\n Trade timeframe: ", trade.timeframe,
            "\n Trade buy tag: ", trade.buy_tag,
            "\n Trade close date: ", trade.close_date,
            "\n Trade close profit: ", trade.close_profit,
            "\n Candle total: \n",candle)
        
        return stoploss_from_absolute(current_rate - (candle['atr'] * 2), current_rate)


    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (qtpylib.crossed_above(dataframe['close'], dataframe['sma'])),
            ['buy', 'buy_tag']] = (1, 'buy_signal_sma_cross')

        # Print the Analyzed pair
        print(f"BUY result for {metadata['pair']}")
        # Inspect the last 5 rows
        print(dataframe[dataframe["buy"]==1].tail())

        return dataframe


    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (qtpylib.crossed_below(dataframe['close'], dataframe['sma'])),
            ['sell', 'sell_tag']] = (1, 'sell_signal_sma_cross')
        
        # Print the Analyzed pair
        print(f"SELL result for {metadata['pair']}")
        # Inspect the last 5 rows
        print(dataframe[dataframe["sell"]==1].tail())

        return dataframe


