from services import *
from services.token_import import TOKEN
from services.cfg import DatabaseId,DatabaseNames
import os
from datetime import timedelta
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now
from progress.bar import Bar
        
if __name__ == '__main__':
    # data = []
    # database = make_shares_database()
    # count = 0
    # for i in range(len(database)):
    #     if count == 5:
    #         break
    #     row = database.loc[i]
    #     with Client(TOKEN) as client:
    #         try:
    #             result = price_analytics(price_tags(row['figi']))
    #             result['name'] = row['name']
    #             data.append(result)
    #         except Exception:
    #             continue
    #     count += 1
    # print(normalize_price(data))``

    # Выше твой код который если раскоментить то будет работать -> зайди в scripts и посмотри че тебе надо переделать чтобы
    # после встроить свою темку вниз:


    # ОЧЕНЬ ВАЖНО!!!!!
    # НАШЕ ЕБЕЙШЕЕ TINKOFF API МОЖЕТ ОБРАБОТАТЬ МАКСИМУМ 600 ЗАПРОСОВ В МИНУТУ, ТО ЕСТЬ В БУДУЩЕМ
    # НАДО БУДЕТ ЕБАНУТЬ ОПТИМИЗАЦИЮ, ЧТОБЫ МЫ НЕ ДЕЛАЛИ ЛИШНИХ ЗАПРОСОВ, А СРАЗУ БРАЛИ ВСЕ ЧТО НУЖНО И ПОТОМ РАСКИДЫВАЛИ ПО ХУЙНЯМ
    # ПЛЮС ТАМ ЗАПРОСЫ ХУЙ ПОЙМИ КАК ИДУТ И ДАЖЕ ОДНА МОЯ АНАЛИТИКА ГДЕ ТОЛЬКО СВЕЧИ ЗАПРАШИВАЮТ 1 РАЗ ЛОМАЕТ ПОЛНЫМ ПРОХОДОМ ПО БАЗЕ ВСЕ К ХУЯМ
    # sleep(0.5) вроде как превентит выход за макс запросов в минуту, но надо искать более оптимальное решение

    database = make_shares_database()
    working_time = Bar('Аналитика данных',max=len(database),suffix='%(percent).1f%% - %(eta)ds')
    for i in range(len(database)):
        inf = database.loc[i][DatabaseId.FIGI]
        database.at[i,DatabaseNames.VOLUME_ANALYZE] = volume_analytic(inf)
        database.at[i,DatabaseNames.FIRST_DAY_ANALYZE] = first_day_analytic(database.loc[i][DatabaseId.FIRST_TRADE_YEAR])
        database.at[i,DatabaseNames.PRICE_ANALYZE] = price_analytics(inf)
        # добавь код для вставки в БД вместо print(database)
        # выше заготовка, которая должна работать после того как ты зарефакторишь свой код


        # напиши функцию нормализации для всего столбика, но не ебашь ее сюда, я сам потом ее встрою в main,
        # твоя задача - просто написать ее
        working_time.next()
    working_time.finish()
    print(normalize(database))