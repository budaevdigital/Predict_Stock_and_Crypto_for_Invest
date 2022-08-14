# messaging/telegram_bot.py
import telegram
from telegram.ext import ConversationHandler, Updater

# Обновляем директорию для импорта встроенных модулей
from os import path
from sys import path as sys_path


current = path.dirname(path.realpath(__file__))
parent = path.dirname(current)
sys_path.append(parent)

from config import settings, date_time
from messaging import navigation as buttons
from database import helpful_func as base
from parse.predict_parse import get_predict_price_1_to_14_days
from parse.parse import (
    get_price_from_binance,
    get_historical_data,
    get_all_cryptos,
)
from graph import graphics_stock

watchlist_position = settings.WATCHLIST_POSITION
bot = telegram.Bot(token=settings.TOKEN)
updater = Updater(token=settings.TOKEN)


# Отправляет сообщение админу, если нужна (пока не используется)
def send_message(message: str) -> None:
    """
    Принимаем и пересылаем текстовое сообщение
    (CHATID задаётся в settings.py)
    """
    bot.send_message(settings.CHAT_ID, message)


def send_photo(name_img: str, user_chat_id: int) -> None:
    """
    Принимаем название графика (в IMG) и пересылаем его
    (CHATID задаётся в settings.py)
    """
    current_img = path.join(settings.IMG_DIR, name_img)
    with open(current_img, "rb") as img:
        bot.send_photo(user_chat_id, img)


def first_starting_messaging(update, context) -> None:
    """
    При первом общении с пользователем (нажатии /start), отсылает
    приветственное сообщение и создаёт нового пользователя в БД
    {
        'username': 'dmitrybudaev',
        'type': 'private',
        'id': 286003757,
        'last_name': 'Budaev',
        'first_name': 'Dmitry'
    }
    """
    # Сохраняем информацию о чате, откоторого пришло сообщение
    user_chat_info = update.effective_chat
    # Узнаем имя нашего пользователя (распарсив запрос update.message)
    user_first_name = update.message.chat.first_name
    # Настроим кнопку для сообщения
    button = buttons.keyboard_main_menu
    try:
        match base.search_existing_field_in_db(
            cryptos="cryptos", symbol="symbol", BTC="BTC"
        ):
            case False:
                all_cryptos = get_all_cryptos()
                base.update_cryptos_list_in_db(all_cryptos)
                settings.logging.info(
                    "Обновлена база всех криптовалют для нового пользователя"
                )
    except Exception as error:
        settings.logging.error(
            f"Ошибка ({error}) при обновлении списка криптовалют в БД "
            "при добавлении нового пользователя"
        )
    try:
        base.create_new_user(
            user_id=update.effective_chat.id,
            first_name=update.message.chat["first_name"],
            last_name=update.message.chat["last_name"],
            username=update.message.chat["username"],
        )
    except Exception as error:
        settings.logging.error(
            f"Ошибка ({error}) при создании пользователя из ТГ бота"
        )
    # и напишем персональное сообщение
    context.bot.send_message(
        chat_id=user_chat_info.id,
        text=(
            f"{user_first_name}, приветствую тебя. "
            "\n"
            "\n"
            "Этот бот предназначен для <b>анализа</b> и "
            "<b>прогназирования</b> цен на криптовалюты. "
            "\n"
            "\n"
            "На отслеживание и прогназированиие, "
            f"можно добавлять <b>до {watchlist_position} криптовалют</b>."
            "\n"
            "[💰 <b><i>Прогноз</i></b>]: получить прогноз цен криптовалюты."
            "\n"
            "[📋 <b><i>Список избранного</i></b>]: редактирование списка "
            "криптовалют."
        ),
        # добавим кнопку к интерфейсу
        reply_markup=button,
        parse_mode="HTML",
    )


def see_menu_home(update, context) -> None:
    user_chat_info = update.effective_chat
    button = buttons.keyboard_main_menu
    context.bot.send_message(
        chat_id=user_chat_info.id,
        text=(
            "\n"
            "[💰 <b><i>Прогноз</i></b>]: получить прогноз цен криптовалюты."
            "\n"
            "[📋 <b><i>Список избранного</i></b>]: редактирование списка "
            "криптовалют."
        ),
        reply_markup=button,
        parse_mode="HTML",
    )


def see_menu_predict(update, context) -> None:
    user_chat_info = update.effective_chat
    button = buttons.keyboard_other_predict_menu
    context.bot.send_message(
        chat_id=user_chat_info.id,
        text=(
            "Прогноз цен:"
            "\n"
            "------------"
            "\n"
            "[🤑 <b><i>Цены</i></b>]: узнать прогноз цен на "
            " выбранную криптовалюту в ближайшие 2 недели."
            "\n"
            "[📈 <b><i>График уровней</i></b>]: графики <b>Low</b> и "
            "<b>High</b> уровней."
        ),
        reply_markup=button,
        parse_mode="HTML",
    )


def see_menu_watchlist(update, context) -> None:
    user_chat_info = update.effective_chat
    button = buttons.keyboard_other_watchlist_menu
    count = 0
    try:
        cryptos_in_watchlist = base.reading_crypto_in_watchlist(
            user_chat_info.id
        )
    except Exception as error:
        settings.logging.error(
            f"Ошибка ({error}) при чтении избранных криптавалют из ТГ"
        )
        cryptos_in_watchlist = [
            (),
        ]
    message = ""
    match cryptos_in_watchlist:
        case False:
            message = "\nСписок избранных пуст!"
            cryptos_in_watchlist = []
        case _:
            for row in range(len(cryptos_in_watchlist)):
                count += 1
                message = (
                    message
                    + "\n"
                    + str(count)
                    + " "
                    + str(cryptos_in_watchlist[row][2])
                )
    context.bot.send_message(
        chat_id=user_chat_info.id,
        text=(
            "Список избранных криптовалют:"
            "\n"
            "------------"
            "\n"
            f"Можно добавить <b>до {watchlist_position} криптовалют</b>"
            "\n"
            "\n"
            f"Сейчас в избранном {len(cryptos_in_watchlist)} криптовалюты:"
            f"{message}"
            "\n"
            "\n"
            "[✅ <b><i>Добавить</i></b>]: добавить криптовалюту на наблюдение."
            "\n"
            "[❌ <b><i>Удалить</i></b>]: удалить криптовалюту из списка "
            "наблюдения."
        ),
        reply_markup=button,
        parse_mode="HTML",
    )


def see_list_crypto_from_watchlist(update, context) -> None:
    user_chat_info = update.effective_chat
    try:
        cryptos_in_watchlist = base.reading_crypto_in_watchlist(
            user_chat_info.id
        )
        match cryptos_in_watchlist:
            case False:
                cryptos_in_watchlist = []
                button = buttons.keyboard_other_watchlist_menu
                msg = (
                    "Список избранного пуст.\n\n[✅ Добавить]: добавить "
                    "криптовалюту на наблюдение."
                )
            case _:
                button = buttons.button_from_crypto_symbol_for_delete(
                    cryptos_in_watchlist
                )
                msg = (
                    "Выберите криптовалюту, которую нужно убрать из списка "
                    "наблюдения 🔽"
                )
    except Exception as error:
        settings.logging.error(
            f"Ошибка ({error}) при показе избранных криптавалют в ТГ"
        )
    context.bot.send_message(
        chat_id=user_chat_info.id,
        text=(
            "Удаление из списка наблюдения:" "\n" "------------" "\n" f"{msg}"
        ),
        reply_markup=button,
        parse_mode="HTML",
    )


def choise_and_delete_crypto_from_watchlist(update, context) -> None:
    user_chat_info = update.effective_chat
    message = update.message.text
    symbol = message.split()
    try:
        base.delete_crypto_from_watch_list(user_chat_info.id, symbol[1])
    except Exception as error:
        settings.logging.error(
            f"Ошибка ({error}) при удалении избранных криптавалют из ТГ"
        )
    cryptos_in_watchlist = base.reading_crypto_in_watchlist(user_chat_info.id)
    match cryptos_in_watchlist:
        case False:
            cryptos_in_watchlist = []
    button = buttons.keyboard_other_watchlist_menu
    context.bot.send_message(
        chat_id=user_chat_info.id,
        text=(
            f"Криптовалюта <b>{symbol[1]}</b> удалена из списка наблюдения!"
            "\n"
            "\n"
            f"Сейчас в избранном <b>{len(cryptos_in_watchlist)}</b> позиции."
            "\n"
            f"Доступны на наблюдение "
            "<b>{watchlist_position - len(cryptos_in_watchlist)}</b> позиций"
            "\n"
            "\n"
            "[✅ <b><i>Добавить</i></b>]: добавить криптовалюту на наблюдение."
            "\n"
            "[❌ <b><i>Удалить</i></b>]: удалить криптовалюту из "
            "списка наблюдения."
        ),
        reply_markup=button,
        parse_mode="HTML",
    )


def see_menu_for_add_crypto(update, context) -> None:
    user_chat_info = update.effective_chat
    context.bot.send_message(
        chat_id=user_chat_info.id,
        text=(
            "Добавление в список наблюдения:"
            "\n"
            "------------"
            "\n"
            "Введите символ криптовалюты (в ответном сообщении), которую "
            "нужно добавить в список наблюдения 🔽"
            "\n"
            "<i>Пример:</i> <b>BTC</b>"
        ),
        reply_markup=telegram.ReplyKeyboardRemove(),
        parse_mode="HTML",
    )
    return "stage_1"


def add_crypto_in_watchlist(update, context) -> None:
    user_chat_info = update.effective_chat
    crypto_symbol = ((update.message.text).replace(" ", "")).upper()
    cryptos_in_watchlist = base.reading_crypto_in_watchlist(user_chat_info.id)
    try:
        match cryptos_in_watchlist:
            case False:
                cryptos_in_watchlist = []
                is_add = base.add_new_crypto_in_db_for_watch(
                    user_chat_info.id, crypto_symbol
                )
                if is_add:
                    msg = (
                        f"Криптовалюта <b>{crypto_symbol}</b> добавлена в "
                        "список наблюдения!"
                    )
                else:
                    msg = (
                        f"Не удалось добавить валюту (<b>{crypto_symbol}</b>)."
                        " Перепроверьте, возможно вы ошиблись в написании?"
                    )
                    try:
                        match base.search_existing_field_in_db(
                            cryptos="cryptos", symbol="symbol", BTC="BTC"
                        ):
                            case False:
                                all_cryptos = get_all_cryptos()
                                base.update_cryptos_list_in_db(all_cryptos)
                                settings.logging.info(
                                    "Обновлена база всех криптовалют для "
                                    "нового пользователя"
                                )
                    except Exception as error:
                        settings.logging.error(
                            f"Ошибка ({error}) при обновлении "
                            "списка криптовалют в БД при "
                            "добавлении нового пользователя"
                        )
            case _:
                if len(cryptos_in_watchlist) < watchlist_position:
                    is_add = base.add_new_crypto_in_db_for_watch(
                        user_chat_info.id, crypto_symbol
                    )
                    if is_add:
                        msg = (
                            f"Криптовалюта <b>{crypto_symbol}</b> добавлена"
                            " в список наблюдения!"
                        )
                    else:
                        msg = (
                            "Хм, не удалось добавить валюту "
                            f"(<b>{crypto_symbol}</b>)."
                            " Перепроверьте, возможно вы ошиблись в написании?"
                        )
                        try:
                            match base.search_existing_field_in_db(
                                cryptos="cryptos", symbol="symbol", BTC="BTC"
                            ):
                                case False:
                                    all_cryptos = get_all_cryptos()
                                    base.update_cryptos_list_in_db(all_cryptos)
                                    settings.logging.info(
                                        "Обновлена база всех криптовалют для "
                                        "нового пользователя"
                                    )
                        except Exception as error:
                            settings.logging.error(
                                f"Ошибка ({error}) при обновлении "
                                "списка криптовалют в БД при "
                                "добавлении нового пользователя"
                            )
                else:
                    msg = (
                        "Список избранного заполнен.\n\nУдалите, "
                        "что-нибудь, перед добавлением!"
                    )
    except Exception as error:
        settings.logging.error(
            f"Ошибка ({error}) при добавлении криптавалют в ТГ"
        )
    button = buttons.keyboard_other_watchlist_menu
    context.bot.send_message(
        chat_id=user_chat_info.id,
        text=(f"{msg}"),
        reply_markup=button,
        parse_mode="HTML",
    )
    return ConversationHandler.END


def get_price_1_to_14_days(update, context) -> None:
    button = buttons.keyboard_other_predict_menu
    user_chat_info = update.effective_chat
    cryptos_in_watchlist = base.reading_crypto_in_watchlist(user_chat_info.id)
    try:
        match cryptos_in_watchlist:
            case False:
                message = (
                    "\nСписок избранных пуст!"
                    f"\nДоступны на наблюдение {watchlist_position} позиций"
                )
                context.bot.send_message(
                    chat_id=user_chat_info.id,
                    text=message,
                    reply_markup=button,
                    parse_mode="HTML",
                )
            case _:
                for count in range(len(cryptos_in_watchlist)):
                    crypto_name = base.search_existing_field_in_db(
                        db_name="cryptos",
                        column_name="symbol",
                        search_field=cryptos_in_watchlist[count][2],
                    )
                    crypros_predict_price = get_predict_price_1_to_14_days(
                        crypto_name[1]
                    )
                    crypros_today_price = get_price_from_binance(
                        symbol=cryptos_in_watchlist[count][2]
                    )
                    message = (
                        f"Прогноз для <b>{crypto_name[1]}</b> на "
                        "ближайшие 2 недели:"
                        "\n"
                        "------------"
                        "\n"
                        "<b>Дата</b> | <b>Стоимость</b>, $"
                        "\n"
                        f"Сегодня | {crypros_today_price} $"
                        "\n"
                        f"{crypros_predict_price}"
                        "\n"
                    )
                    context.bot.send_message(
                        chat_id=user_chat_info.id,
                        text=message,
                        reply_markup=button,
                        parse_mode="HTML",
                    )
    except Exception as error:
        settings.logging.error(
            f"Ошибка ({error}) при запросе предсказания цен криптавалют в ТГ"
        )


def see_choice_graph_level(update, context) -> None:
    user_chat_info = update.effective_chat
    button = buttons.keyboard_other_level_menu
    context.bot.send_message(
        chat_id=user_chat_info.id,
        text=(
            "Графики уровней цен:"
            "\n"
            "------------"
            "\n"
            "[🔴 <b><i>Low</i></b>]: Уровень поддержки при падении"
            "\n"
            "[🟢 <b><i>High</i></b>]: Уровень сопротивления при росте"
        ),
        reply_markup=button,
        parse_mode="HTML",
    )


def get_high_level_graph(
    update, context, name_levels="High", func_message="Верхних уровней"
) -> None:
    user_chat_info = update.effective_chat
    button = buttons.keyboard_other_level_menu
    try:
        dict_date = date_time.set_current_to_from_date()
    except Exception as error:
        settings.logging.error(
            f"Ошибка ({error}) при запросе даты при отрисовки графиков в ТГ"
        )
    cryptos_in_watchlist = base.reading_crypto_in_watchlist(user_chat_info.id)
    match cryptos_in_watchlist:
        case False:
            message = (
                "\nСписок избранных пуст!"
                f"\nДоступны на наблюдение {watchlist_position} позиций"
            )
            context.bot.send_message(
                chat_id=user_chat_info.id,
                text=message,
                reply_markup=button,
                parse_mode="HTML",
            )
        case _:
            try:
                for count in range(len(cryptos_in_watchlist)):
                    crypto_name = base.search_existing_field_in_db(
                        db_name="cryptos",
                        column_name="symbol",
                        search_field=cryptos_in_watchlist[count][2],
                    )
                    df = get_historical_data(
                        symbol=crypto_name[1],
                        from_date=dict_date["old-date"],
                        today_date=dict_date["today"],
                        is_crypto=True,
                        country=settings.COUNTRY,
                    )
                    img_name = graphics_stock.stock_to_graph(
                        df=df,
                        from_date=dict_date["old-date"],
                        today_date=dict_date["today"],
                        stock=crypto_name[1],
                        function=name_levels,
                    )
                    context.bot.send_message(
                        chat_id=user_chat_info.id,
                        text=(
                            f"График {func_message} поддержки у "
                            f"<b>{cryptos_in_watchlist[count][2]}</b>:"
                            "\n"
                        ),
                        reply_markup=button,
                        parse_mode="HTML",
                    )
                    send_photo(img_name, user_chat_info.id)
            except Exception as error:
                settings.logging.error(
                    f"Ошибка ({error}) при запросе даты при отрисовки "
                    "графиков в ТГ"
                )


# Просто переиспользуем функцию для отрисовки графиков
def get_low_level_graph(update, context) -> None:
    get_high_level_graph(
        update=update,
        context=context,
        name_levels="Low",
        func_message="Нижних уровней",
    )
