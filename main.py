from services import *
from services.token_import import TOKEN
from services.cfg import DatabaseId,DatabaseNames
import os
from datetime import timedelta
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now
from progress.bar import Bar
        
if __name__ == '__main__':
    database = make_shares_database()
    working_time = Bar('Аналитика данных',max=len(database),suffix='%(percent).1f%% - %(eta)ds')
    for i in range(len(database)):
        inf = database.loc[i][DatabaseId.FIGI]
        database.at[i,DatabaseNames.VOLUME_ANALYZE] = volume_analytic(inf)
        database.at[i,DatabaseNames.FIRST_DAY_ANALYZE] = first_day_analytic(database.loc[i][DatabaseId.FIRST_TRADE_YEAR])
        database.at[i,DatabaseNames.PRICE_ANALYZE] = price_analytics(inf)
        working_time.next()
    working_time.finish()
    print(normalize(database))