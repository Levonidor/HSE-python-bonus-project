from .cfg import TARGET_COLUMNS
from datetime import timedelta
import pandas as pd
from tinkoff.invest import CandleInterval, Client, InstrumentStatus
from tinkoff.invest.utils import now
from .token_import import TOKEN
from time import sleep
import time
import numpy as np

def make_shares_database() -> pd.DataFrame:
    with Client(TOKEN) as client:
        shares = [i for i in client.instruments.shares().instruments if i.currency == "rub"]
    
    shares_dataframe = pd.DataFrame(columns=TARGET_COLUMNS)
    for i, share in enumerate(shares):
        shares_dataframe.loc[i] = pd.Series(
            (share.figi, share.ticker, share.lot, share.name, share.sector,share.first_1day_candle_date.year,0,0,0), TARGET_COLUMNS
        )
    
    return shares_dataframe

def volume_analytic(figi_: str) -> float:
    share_volume = []
    with Client(TOKEN) as client:
        sleep(0.5)
        for candle in client.get_all_candles(
            figi=figi_,
            from_=now() - timedelta(days=(365*5)),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        ):
            share_volume.append(int(candle.volume))
        period = []
        all_periods = []
        for volume in share_volume:
            if len(period) == len(share_volume)//5:
                all_periods.append(sum(period))
                period = []
            else:
                period.append(volume)
        procent_all_periods = []
        for i in range(1,len(all_periods)):
            procent_all_periods.append((all_periods[i]-all_periods[i-1])/(all_periods[i-1]/100))
    return sum(procent_all_periods)/len(procent_all_periods)

def price_analytics(st) -> float():
    with Client(TOKEN) as client:
        sp = []
        for candle in client.get_all_candles(
            figi= st,
            from_=now() - timedelta(days=365 * 5),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        ):
            sp.append(candle.close.units)
    count = 0
    for i in range(len(sp) - 1):
        if sp[i] >= sp[i+1]:
            count += 1
    try:
        return ((sum(sp) / len(sp) / sp[0] * 100) - 100 + count / len(sp) * 100) / 100
    except Exception:
        return 0.0
    


def normalize(database: pd.DataFrame) -> pd.DataFrame:
    normalized_database = database.copy()
    columns_to_normalize = ["VOLUME_ANALYZE", "FIRST_DAY_ANALYZE", "PRICE_ANALYZE"]
    
    for column in columns_to_normalize:
        normalized_database[column] = (normalized_database[column] - normalized_database[column].min()) / (normalized_database[column].max() - normalized_database[column].min())
    
    return normalized_database

def first_day_analytic(year: int) -> int:
    return int(time.localtime().tm_year)-year
