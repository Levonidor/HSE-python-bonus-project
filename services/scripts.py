from .cfg import TARGET_COLUMNS, DatabaseId, DatabaseNames, CandeCallId
from datetime import timedelta
import pandas as pd
from tinkoff.invest import CandleInterval, Client, InstrumentStatus
from tinkoff.invest.utils import now
from time import sleep
import time
import numpy as np
from functools import lru_cache


from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

def make_shares_database() -> pd.DataFrame:
    with Client(TOKEN) as client:
        shares = [
            i for i in client.instruments.shares().instruments if i.currency == "rub"
        ]

    shares_dataframe = pd.DataFrame(columns=TARGET_COLUMNS)
    for i, share in enumerate(shares):
        shares_dataframe.loc[i] = pd.Series(
            (
                share.figi,
                share.ticker,
                share.lot,
                share.name,
                share.sector,
                share.first_1day_candle_date.year,
                0,
                0,
                0,
                0,
                0,
            ),
            TARGET_COLUMNS,
        )

    return shares_dataframe


def candle_call(figi_: str) -> list[list, list]:
    share_volumes = []
    share_prices = []
    shares_units_nano_prices = []
    with Client(TOKEN) as client:
        for candle in client.get_all_candles(
            figi=figi_,
            from_=now() - timedelta(days=(365)),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        ):
            share_volumes.append(int(candle.volume))
            share_prices.append(candle.close.units)
            shares_units_nano_prices.append(
                float(f"{candle.close.units}.{candle.close.nano}")
            )
    return share_prices, share_volumes, shares_units_nano_prices


def nowaday_price(share_prices: list) -> float:
    return share_prices[-1]


def volume_analytic(share_volume: list) -> float:
    period = []
    all_periods = []
    for volume in share_volume:
        if len(period) == len(share_volume) // 5:
            all_periods.append(sum(period))
            period = []
        else:
            period.append(volume)
    procent_all_periods = []
    for i in range(1, len(all_periods)):
        procent_all_periods.append(
            (all_periods[i] - all_periods[i - 1]) / (all_periods[i - 1] / 100)
        )
    return sum(procent_all_periods) / len(procent_all_periods)


def price_analytics(share_prices: list) -> float:
    count = 0
    for i in range(0, len(share_prices) - 1):
        if share_prices[i] >= share_prices[i + 1]:
            count += 1
    try:
        return (
            (
                (sum(share_prices) / len(share_prices) / share_prices[0] * 100) * 0.2
                + (count / len(share_prices) * 100) / 100
            )
            * 0.8
        ) / 2
    except Exception:
        return 0.0


def normalize(database: pd.DataFrame, columns_to_normalize: list) -> pd.DataFrame:
    normalized_database = database.copy()

    for column in columns_to_normalize:
        normalized_database[column] = (
            normalized_database[column] - normalized_database[column].min()
        ) / (normalized_database[column].max() - normalized_database[column].min())

    return normalized_database


def first_day_analytic(year: int) -> int:
    return int(time.localtime().tm_year) - year


def overall_analytic(database: pd.DataFrame) -> pd.DataFrame:
    database = normalize(
        database,
        [
            DatabaseNames.VOLUME_ANALYZE,
            DatabaseNames.FIRST_DAY_ANALYZE,
            DatabaseNames.PRICE_ANALYZE,
        ],
    )
    for i in range(len(database)):
        database.at[i, DatabaseNames.OVERALL_ANALYZE] = (
            database.loc[i][DatabaseId.VOLUME_ANALYZE] * 0.2
            + database.loc[i][DatabaseId.PRICE_ANALYZE] * 0.7
            + database.loc[i][DatabaseId.FIRST_DAY_ANALYZE] * 0.1
        )
    database = database.sort_values(by=DatabaseNames.OVERALL_ANALYZE, ascending=False)
    database = normalize(database, [DatabaseNames.OVERALL_ANALYZE])
    return database


def csv_file(database: pd.DataFrame) -> None:
    import csv
    import os

    if os.path.exists("./telegram/data.csv"):
        os.remove("./telegram/data.csv")
    with open("./telegram/data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(TARGET_COLUMNS)
        for i in range(len(database)):
            row = database.iloc[i].to_list()
            writer.writerow(row)


def check_date(a, b) -> bool:
    for i in range(2, 0, -1):
        if a[i] <= b[i]:
            continue
        else:
            break
    if i == 0:
        return True
    return False
