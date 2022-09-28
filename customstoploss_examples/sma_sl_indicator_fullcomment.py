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
from datetime import datetime, timedelta
from freqtrade.persistence import Trade
from freqtrade.strategy import stoploss_from_absolute, stoploss_from_open
from freqtrade.exchange import timeframe_to_prev_date

class sma_sl_indicator_fullcomment(IStrategy):
    timeframe = "1d"
    # Both stoploss and roi are set to 100 to prevent them to give a sell signal.
    stoploss = -0.05
    minimal_roi = {"0": 100}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # sma
        dataframe['sma'] = ta.SMA(dataframe, timeperiod=50)

        # parabolic SAR for custom stoploss
        dataframe['sar'] = ta.SAR(dataframe)

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

        # You may access dataframe in various strategy functions by querying it from dataprovider.
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        # Obtain last available candle. Do not use current_time to look up latest candle, because 
        # current_time points to current incomplete candle whose data is not available.
        last_candle = dataframe.iloc[-1].squeeze()
        # In dry/live runs trade open date will not match candle open date therefore it must be 
        # rounded.
        trade_date = timeframe_to_prev_date(self.timeframe, trade.open_date_utc)
        # Look up trade candle.
        trade_candle = dataframe.loc[dataframe['date'] == trade_date]
        # trade_candle may be empty for trades that just opened as it is still incomplete.
        if not trade_candle.empty:
            trade_candle = trade_candle.squeeze()

        # Use parabolic sar as absolute stoploss price
        stoploss_price = last_candle['sar']

        # Convert absolute price to percentage relative to current_rate
        if stoploss_price < current_rate:
            return (stoploss_price / current_rate) - 1

        print("\n Pair: ",pair,
            "\n Trade: ", trade,
            "\n Current time: ", current_time,
            "\n Current rate: ", current_rate,
            "\n Custom stoploss price: ", stoploss_price,
            "\n Current profit: ", current_profit,
            "\n Trade open date UTC: ", trade.open_date_utc, 
            "\n Timedelta 120: ", current_time - timedelta(minutes=120),
            "\n Timedelta 60: ", timedelta(minutes=60), 
            "\n Trade amount: ", trade.amount, 
            "\n Trade buy tag: ", trade.buy_tag, 
            "\n Trade fee open: ", trade.fee_open, 
            "\n Trade fee open currency: ", trade.fee_open_currency,
            "\n Trade initial stoploss: ", trade.initial_stop_loss, 
            "\n Trade initial stoploss percent: ", trade.initial_stop_loss_pct, 
            "\n Trade stoploss: ", trade.stop_loss, 
            "\n Trade stoposs percent: ", trade.stop_loss_pct, 
            "\n Trade open rate: ", trade.open_rate, 
            "\n Trade open trade value: ", trade.open_trade_value,
            "\n Trade amount requested: ", trade.amount_requested,
            "\n Trade exchange: ", trade.exchange,
            "\n Trade is open: ", trade.is_open,
            "\n Trade strategy: ", trade.strategy,
            "\n Trade timeframe: ", trade.timeframe,
            "\n Trade stake amount: ", trade.stake_amount, 
            "\n Trade use db: ", trade.use_db,
            "\n Trade total profit: ", trade.total_profit,
	    "\n Last candle from dataframe: ", last_candle,
	    "\n Trade date from dataframe: ", trade_date,
	    "\n Trade candle from dataframe: ", trade_candle,
	    "\n Stoploss price from dataframe: ", stoploss_price,
	    "\n Dataframe: ", dataframe)

        # return maximum stoploss value, keeping current stoploss price unchanged
        return 1

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            # (qtpylib.crossed_above(dataframe['close'], dataframe['sma'])),
            (dataframe['close'] > dataframe['sma']),
             ['buy', 'buy_tag']] = (1, 'buy_signal_sma_cross')

        return dataframe


    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (qtpylib.crossed_below(dataframe['close'], dataframe['sma'])),
            "sell",
            ] = 1
        return dataframe

