from datetime import timedelta
import pandas as pd
import numpy as np
from .tg_cfg import *


def read_csv(relevant_parametr: float) -> pd.DataFrame:
    database = pd.DataFrame(columns=TARGET_COLUMNS)
    with open('./telegram/data.csv','r') as csv:
        minus_index = -1
        for i, info in enumerate(csv):
            if i == 0:
                pass
            else:
                try:
                    database.loc[i+minus_index] = pd.Series(tuple(info.split(',')),TARGET_COLUMNS)
                except Exception:
                    try:
                        database.loc[i+minus_index] = pd.Series(tuple(info.split(',')[0:3]+[''.join(info.split(',')[3:-7])]+info.split(',')[-7:]),TARGET_COLUMNS)
                    except Exception:
                        minus_index -= 1
        database = dataframe_col_to_float(database,[DatabaseNames.OVERALL_ANALYZE,DatabaseNames.NOWADAY_PRICE])
    return make_buying_database(database, relevant_parametr)

def dataframe_col_to_float(database: pd.DataFrame, columns: list) -> pd.DataFrame:
    for col in columns:
        database[col] = pd.Series(map(float,database[col]))
    return database

def make_buying_database(database: pd.DataFrame, relevant_parametr: float) -> pd.DataFrame:
    buying_database = pd.DataFrame(columns=BUYER_COLUMNS)
    index = 0
    for i in range(len(database)):
        if database.loc[i][DatabaseNames.OVERALL_ANALYZE] >= relevant_parametr:
            buying_database.loc[index] = pd.Series((database.loc[i][DatabaseNames.NAME],database.loc[i][DatabaseNames.TICKER],database.loc[i][DatabaseNames.OVERALL_ANALYZE],database.loc[i][DatabaseNames.NOWADAY_PRICE]),BUYER_COLUMNS)
            index += 1
    return buying_database

def add_recommendated_share(recommendated_shares: pd.DataFrame, share: pd.Series, amount: int) -> pd.DataFrame:
    index = len(recommendated_shares)
    if share[DatabaseNames.TICKER] not in recommendated_shares[RecommendNames.TICKER].tolist():
        recommendated_shares.loc[index] = pd.Series((share[DatabaseNames.TICKER],amount,share[DatabaseNames.NOWADAY_PRICE],amount*share[DatabaseNames.NOWADAY_PRICE],share[DatabaseNames.NAME]),RECOMMEND_COLUMNS)
    else:
        for i in range(len(recommendated_shares)):
            if recommendated_shares.loc[i][RecommendNames.TICKER]==share[DatabaseNames.TICKER]:
                ind = i
                break
        recommendated_shares.loc[ind] = pd.Series((share[DatabaseNames.TICKER],amount+recommendated_shares.loc[ind][RecommendNames.AMOUNT],share[DatabaseNames.NOWADAY_PRICE],(amount+recommendated_shares.loc[ind][RecommendNames.AMOUNT])*share[DatabaseNames.NOWADAY_PRICE],share[DatabaseNames.NAME]),RECOMMEND_COLUMNS)


def buy_shares(budget: int, relevant_parametr: float) -> list[pd.DataFrame,float]:
    database = read_csv(relevant_parametr)
    print(database)
    print(len(database))
    recommendated_shares = pd.DataFrame(columns=RECOMMEND_COLUMNS)
    now_budget = budget
    while True:
        if now_budget - min(database[DatabaseNames.NOWADAY_PRICE]) < 0:
            break
        for i in range(len(database)):
            if now_budget-((budget//100)//(database.loc[i][DatabaseNames.NOWADAY_PRICE])*(database.loc[i][DatabaseNames.NOWADAY_PRICE])) >= 0 and ((budget//100)//(database.loc[i][DatabaseNames.NOWADAY_PRICE])) > 0:
                add_recommendated_share(recommendated_shares,database.loc[i],((budget//100)//(database.loc[i][DatabaseNames.NOWADAY_PRICE])))
                now_budget -= ((budget//100)//(database.loc[i][DatabaseNames.NOWADAY_PRICE])*(database.loc[i][DatabaseNames.NOWADAY_PRICE]))
            elif (now_budget-(now_budget//(database.loc[i][DatabaseNames.NOWADAY_PRICE])*(database.loc[i][DatabaseNames.NOWADAY_PRICE]))) >= 0 and (now_budget//(database.loc[i][DatabaseNames.NOWADAY_PRICE])*(database.loc[i][DatabaseNames.NOWADAY_PRICE])) < budget/10 and (now_budget//(database.loc[i][DatabaseNames.NOWADAY_PRICE])*(database.loc[i][DatabaseNames.NOWADAY_PRICE])) > 0:
                add_recommendated_share(recommendated_shares,database.loc[i],(now_budget//(database.loc[i][DatabaseNames.NOWADAY_PRICE])))
                now_budget -= (now_budget//(database.loc[i][DatabaseNames.NOWADAY_PRICE])*(database.loc[i][DatabaseNames.NOWADAY_PRICE]))
            elif now_budget-database.loc[i][DatabaseNames.NOWADAY_PRICE] >= 0 and database.loc[i][DatabaseNames.NOWADAY_PRICE] < budget/100*30:
                add_recommendated_share(recommendated_shares,database.loc[i], 1)
                now_budget -= database.loc[i][DatabaseNames.NOWADAY_PRICE]
        print(now_budget)

    print(recommendated_shares)
    return [recommendated_shares,round(now_budget,2)]