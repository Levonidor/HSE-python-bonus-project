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
    database = normalize(database)
    for i in range(len(database)):
        database.at[i,DatabaseNames.OVERALL_ANALYZE] = database.loc[i][DatabaseId.VOLUME_ANALYZE] * 0.4 + database.loc[i][DatabaseId.PRICE_ANALYZE] * 0.5 + database.loc[i][DatabaseId.FIRST_DAY_ANALYZE] * 0.1
    database = database.sort_values(by=database.columns[-1], ascending=False)
    print(database)