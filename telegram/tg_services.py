from datetime import timedelta
import pandas as pd
import numpy as np
from .tg_cfg import *
import matplotlib.pyplot as plt



def read_csv(relevant_parametr: float) -> pd.DataFrame:
    database = pd.DataFrame(columns=TARGET_COLUMNS)
    with open('./telegram/data.csv','r',encoding='utf-8') as csv:
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
    make_vizualization(recommendated_shares)
    return [recommendated_shares,round(now_budget,2)]

def make_vizualization(recommendated_shares: pd.DataFrame) -> None:
    plt.figure(figsize=(15,15))
    plt.pie(recommendated_shares[RecommendNames.TOTAL_PRICE],labels=recommendated_shares[RecommendNames.TICKER])
    plt.savefig('./telegram/pie_shares.png')
    
    
def csv_file_(database: pd.DataFrame) -> None:
    import csv
    import os
    if os.path.exists('./telegram/stocks.csv'):
        os.remove('./telegram/stocks.csv')
    with open('./telegram/stocks.csv', 'w', newline='',encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(RECOMMEND_COLUMNS)
        for i in range(len(database)):
            row = database.loc[i].to_list()
            writer.writerow(row)
    
            
router = Router()     
options = []
class update_inf(StatesGroup):
    risk = State()
    amount = State()
    
    
@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer("Привет! Я твой личный ассистент по инвестициям")
    kb = ReplyKeyboardBuilder()
    kb.button(text="0.1")
    kb.button(text="0.2")
    kb.button(text="0.3")
    kb.button(text="0.4")
    kb.button(text="0.5")
    kb.button(text="0.6")
    kb.button(text="0.7")
    kb.button(text="0.8")
    kb.button(text="0.9")
    kb.button(text="1")
    kb.adjust(5, 5)
    await msg.answer("Для начала выбери насколько рискованную стратегию ты хочешь выбрать: где 0 - это самые волатильные акции, а 1 - самые стабильные", reply_markup=kb.as_markup(resize_keyboard=True))
    await state.set_state(update_inf.risk)
    
    
@router.message(update_inf.risk)
async def start_handler(msg: Message, state: FSMContext):
    await state.update_data(risk=msg.text)
    data = await state.get_data()
    vol = data['risk']
    while not (0 <= float(vol) <= 1):
        await msg.answer('Кажется что-то пошло не так, попробуйте снова выбрать значение в пределах [0, 1]')
        await state.update_data()
        data = await state.get_data(risk=msg.text)
        vol = data['risk']
    options.append(float(vol))
    await msg.answer("Отлично! Теперь введи свой бюджет в рублях:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(update_inf.amount)


@router.message(update_inf.amount)
async def start_handler(msg: Message, state: FSMContext):
    await state.update_data(amount=msg.text)
    data = await state.get_data()
    rub = data['amount']
    rub = rub.replace(' ', '')
    options.append(float(rub))
    await msg.answer("Подождите немного, происходит магия")
    to_buy = buy_shares(options[1],options[0])
    csv_file_(to_buy[0])
    await msg.answer_document(document=FSInputFile('./telegram/stocks.csv'))
    await msg.answer_document(document=FSInputFile('./telegram/pie_shares.png'))
    await msg.answer('После проведенного анализа я составил портфель из девирсифицированных активов, основываясь на вашей желаемой стратегии')
    await msg.answer('Желаю удачи, буду ждать вас, когда решите обновить портфель')
    options.clear()
    await state.clear()