from typing import Union
import sqlite3
from os import path
from sys import path as sys_path
# Обновляем директорию для импорта модуля
current = path.dirname(path.realpath(__file__))
parent = path.dirname(current)
sys_path.append(parent)

from config import settings

def get_bd_connection():
    connect = sqlite3.connect(settings.DATABASE)
    return connect

def search_existing_field_in_db(db_name: str, 
                            column_name: str, 
                            search_field: Union[str, int]) -> Union[tuple, bool]:
    """
    Проверяет, существует ли указанная запись в БД. Если она есть, возвращает её 
    по указанным в аргументах параметрам.
    ### Аргумент:
        `db_name`(str): - принимает название базы данных
        (в контексте этой программы их может быть 4шт:
            users, cryptos, watch_cryptos, price_cryptos)
        `column_name`(str): - название колонки в БД для поиска
        `search_field`(str, int): значение для поиска
    ### Возвращает:
        bool: `False` - когда значение в БД не найдено
        tuple: - кортеж со значениями из указанной БД
    ### Исключения:
        `OperationalError`: в случае, если БД или колонки в БД 
            не существует
    """
    connect = get_bd_connection()
    cursor = connect.cursor()
    try:
        sql_request = f"SELECT * FROM {db_name} WHERE {column_name}=?"
        cursor.execute(sql_request, (search_field,))
        # fetcall() - найдёт все совпадения
        result =  cursor.fetchone()
    except sqlite3.OperationalError as OperationalError:
        print(OperationalError)
        connect.close()
        return False        
    match result:
        case None:
            connect.close()
            return False
        case _:
            connect.close()
            return result

def update_cryptos_list_in_db(lists_cryptos: dict[str, str]) -> bool:
    """
    Обновляет список криптовалют в БД (columns=['name', 'symbol'])
    ### Аргумент:
        `lists_cryptos`(dict[str, str]): - список криптовалют из парсинга
    ### Возвращает:
        bool: `True` - если хотя-бы одно значение было добавлено
              `False` - если нечего не было добавлено
    ### Исключения:
        `IntegrityError`: в случае, если в БД уже существует запись
    """
    is_update = False
    connect = get_bd_connection()
    cursor = connect.cursor()
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS cryptos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            symbol TEXT UNIQUE);
        """)
    except Exception as error:
        print(error)
    for count in range(len(lists_cryptos)):
        if lists_cryptos[count]['name'] and lists_cryptos[count]['symbol']:
            name = str(lists_cryptos[count]['name'])
            symbol = str(lists_cryptos[count]['symbol']).upper()
            data = (name, symbol)
            try:
                cursor.executemany("INSERT INTO cryptos (name, symbol) VALUES(?, ?);", [data])
            except sqlite3.IntegrityError as IntegrityError:
                continue
            is_update = True
    # применение всех изменений в таблицах БД
    connect.commit()
    connect.close()
    return is_update

def create_new_user(user_id: int, first_name: str, 
                    last_name: str, username: str) -> bool:
    """
    Создаёт нового пользователя в БД. В качестве аргументов, принимает параметры
    из ответа ТГ бота.
    ### Аргумент:
        `user_id`(int): ID пользователя в ТГ
        `first_name`(str): Имя пользователя
        `last_name`(str): Фамилия пользователя
        `username`(str): Юзернейм пользователя в ТГ
    ### Возвращает:
        bool: `True` - в случае, если пользователь создан или уже существует или 
              `False` - когда что-то произошло при создании пользователя
    ### Исключения:
        `IntegrityError`: в случае, если пользователь существует
    """
    add_user = (username, first_name, last_name, user_id)
    if search_existing_field_in_db(db_name='users',):
        return True
    connect = get_bd_connection()
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        firstname TEXT,
        lastname TEXT,
        userid INTEGER UNIQUE);
    """)
    # если данных для записи много, то нужно использовать 
    # 'executemany' вместо обычной 'execute'
    try:
        # поддерживается также и такой стиль "select * from lang where first=:year", {"year": 1972})
        cursor.execute("INSERT INTO users (username, firstname, lastname, userid) VALUES(?, ?, ?, ?);", (add_user))
    except sqlite3.IntegrityError as error:
        print(f'Ошибка {error} - такой пользователь уже существует!')
        connect.close()
        return False
    # применение всех изменений в таблицах БД
    connect.commit()
    connect.close()
    return True

def search_duplicate_watch_crypto(cryptos_id: int, user_id: int) -> bool:
    connect = get_bd_connection()
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM watch_cryptos WHERE cryptos_id = ? AND user_id = ?;", (cryptos_id, user_id))
    result =  cursor.fetchone()
    match result:
        case None:
            connect.close()
            return False
        case _:
            connect.close()
            return True

def add_new_crypto_in_db_for_watch(userid: int, symbol: str) -> bool:
    connect = get_bd_connection()
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS watch_cryptos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cryptos_id INTEGER,
        cryptos_symbol TEXT,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(cryptos_id) REFERENCES cryptos(id),
        FOREIGN KEY(user_id) REFERENCES users(id));
    """)
    user = search_existing_field_in_db(db_name='users', 
                                       column_name='userid', 
                                       search_field=userid)
    symbol = search_existing_field_in_db(db_name='cryptos', 
                                       column_name='symbol', 
                                       search_field=symbol)
    if user and symbol:
        is_duplicate = search_duplicate_watch_crypto(symbol[0], user[0])
        if not is_duplicate:
            try:
                cursor.execute("INSERT INTO watch_cryptos (cryptos_id, cryptos_symbol, user_id) VALUES(?, ?, ?);", (symbol[0], symbol[2], user[0]))
            except sqlite3.IntegrityError as error:
                print(f'Ошибка {error} - такой пользователь уже существует!')
                connect.close()
                return False
            # применение всех изменений в таблицах БД
            connect.commit()
            connect.close()
            return True
    return False

def reading_crypto_in_watchlist(tg_user_id: int):
    connect = get_bd_connection()
    cursor = connect.cursor()
    cursor.execute("""SELECT * FROM watch_cryptos
        WHERE user_id IN (SELECT id FROM users
        WHERE userid=?);""", (tg_user_id, ))
    # fetcall() - найдёт все совпадения
    result =  cursor.fetchall()
    return result
