from services import *
from services.token_import import TOKEN
import os
from datetime import timedelta
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now


    
def price_tags(st):
    with Client(TOKEN) as client:
        sp = []
        for candle in client.get_all_candles(
            figi= st,
            from_=now() - timedelta(days=365 * 5),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        ):
            sp.append(candle.close.units)
    return sp


def price_analytics(lst: list):
    count = 0
    lst1 = lst.copy()
    for i in range(len(lst) - 1):
        if lst[i] >= lst[i+1]:
            count += 1
            
    return {
        'name': '',
        'average': (sum(lst) / len(lst) / lst[0] * 100) - 100,
        'trend': count / len(lst) * 100,
    }

def normalize_price(lst: list[dict]):
    lst1 = []
    for el in lst:
        lst1.append((el['average'], el['trend'], el['name']))
    lst1 = sorted(lst1, key=lambda x: (-x[1], -x[0], x[2]))
    return lst1
    
    
        
if __name__ == '__main__':
    data = []
    database = make_shares_database(TOKEN)
    count = 0
    for i in range(len(database)):
        if count == 5:
            break
        row = database.loc[i]
        with Client(TOKEN) as client:
            try:
                result = price_analytics(price_tags(row['figi']))
                result['name'] = row['name']
                data.append(result)
            except Exception:
                continue
        count += 1
    print(normalize_price(data))

    