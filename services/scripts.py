from .cfg import TARGET_COLUMNS
from datetime import timedelta
import pandas as pd
from tinkoff.invest import CandleInterval, Client, InstrumentStatus
from tinkoff.invest.utils import now

def make_shares_database(TOKEN: str) -> pd.DataFrame:
    with Client(TOKEN) as client:
        shares = [i for i in client.instruments.shares().instruments if i.currency == "rub"]
    
    shares_dataframe = pd.DataFrame(columns=TARGET_COLUMNS)
    for i, share in enumerate(shares):
        shares_dataframe.loc[i] = pd.Series(
            (share.figi, share.ticker, share.lot, share.name, share.sector), TARGET_COLUMNS
        )
    
    return shares_dataframe