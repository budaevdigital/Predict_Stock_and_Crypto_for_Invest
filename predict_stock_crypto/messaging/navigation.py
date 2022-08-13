# messaging/navigation.py
from telegram import ReplyKeyboardMarkup, KeyboardButton

# Настройка кнопки для возвращения в Главное меню
btn_back_to_main = KeyboardButton("◀ Назад в Меню")
keyboard_back_home = ReplyKeyboardMarkup(
    keyboard=([[btn_back_to_main]]), resize_keyboard=True
)

# Главное меню
btn_predict = KeyboardButton("💰 Прогноз")
btn_watch_list = KeyboardButton("📋 Список избранного")
keyboard_main_menu = ReplyKeyboardMarkup(
    keyboard=([[btn_predict, btn_watch_list]]), resize_keyboard=True
)

# Меню "Прогноз"
btn_info_money = KeyboardButton("🤑 Цены")
btn_graph_crypto = KeyboardButton("📈 График уровней")
keyboard_other_predict_menu = ReplyKeyboardMarkup(
    keyboard=([[btn_info_money, btn_graph_crypto], [btn_back_to_main]]),
    resize_keyboard=True,
)

# Меню "Избранное"
btn_add_to_watch = KeyboardButton("✅ Добавить")
btn_delete_to_watch = KeyboardButton("❌ Удалить")
keyboard_other_watchlist_menu = ReplyKeyboardMarkup(
    keyboard=([[btn_add_to_watch, btn_delete_to_watch], [btn_back_to_main]]),
    resize_keyboard=True,
)

# Меню "График уровней"
btn_low_level = KeyboardButton("🔴 Low")
btn_high_level = KeyboardButton("🟢 High")
keyboard_other_level_menu = ReplyKeyboardMarkup(
    keyboard=([[btn_low_level, btn_high_level], [btn_back_to_main]]),
    resize_keyboard=True,
)


# Формирование клавиатуры из списка криптовалют
def button_from_crypto_symbol_for_delete(list_cryptos: list):
    """
    Функция, для отрисовки кнопок в 3 колонки, в зависимости от количества
    элементов в переданном списке
    """
    if len(list_cryptos) != 0:
        row_in_column = 3
        column = (len(list_cryptos) + (row_in_column - 1)) // row_in_column
        button = [[] * row_in_column for i in range(0, column)]
        name_button = {}
        for row in range(len(list_cryptos)):
            name_button[row] = KeyboardButton("➖ " + str(list_cryptos[row][2]))
            button[row // row_in_column].append(name_button[row])
        button.append([btn_back_to_main])
        return ReplyKeyboardMarkup(
            keyboard=(button), resize_keyboard=True
        )
