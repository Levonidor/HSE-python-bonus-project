from .cfg import TARGET_COLUMNS
from datetime import timedelta
import pandas as pd
from tinkoff.invest import CandleInterval, Client, InstrumentStatus
from tinkoff.invest.utils import now
from .token_import import TOKEN

def make_shares_database() -> pd.DataFrame:
    with Client(TOKEN) as client:
        shares = [i for i in client.instruments.shares().instruments if i.currency == "rub"]
    
    shares_dataframe = pd.DataFrame(columns=TARGET_COLUMNS)
    for i, share in enumerate(shares):
        shares_dataframe.loc[i] = pd.Series(
            (share.figi, share.ticker, share.lot, share.name, share.sector,share.first_1day_candle_date), TARGET_COLUMNS
        )
    
    return shares_dataframe

def volume_analytic(figi_: str) -> str:
    share_volume = []
    with Client(TOKEN) as client:
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