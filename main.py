from services import *
from services.token_import import TOKEN


# Запустить адекватно в scripts прогу не получится, надо там писать фукнции и здесь их запускать и бла бла бла
# Короче не еблан - разберешься. 


if __name__ == '__main__':
    database = make_shares_database(TOKEN)
    print(database)