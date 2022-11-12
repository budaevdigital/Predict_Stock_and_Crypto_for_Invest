# main.py
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    Filters,
)
from messaging import telegram_bot as tg_bot
from config import settings


def main():
    try:
        tg_bot.updater.dispatcher.add_handler(
            CommandHandler("start", tg_bot.first_starting_messaging)
        )
        tg_bot.updater.dispatcher.add_handler(
            MessageHandler(Filters.text("💰 Прогноз"), tg_bot.see_menu_predict)
        )
        tg_bot.updater.dispatcher.add_handler(
            MessageHandler(
                Filters.text("◀ Назад в Меню"), tg_bot.see_menu_home
            )
        )
        tg_bot.updater.dispatcher.add_handler(
            MessageHandler(
                Filters.text("📋 Список избранного"), tg_bot.see_menu_watchlist
            )
        )
        tg_bot.updater.dispatcher.add_handler(
            MessageHandler(
                Filters.text("❌ Удалить"),
                tg_bot.see_list_crypto_from_watchlist,
            )
        )
        tg_bot.updater.dispatcher.add_handler(
            MessageHandler(
                Filters.regex("➖ "),
                tg_bot.choise_and_delete_crypto_from_watchlist,
            )
        )
        tg_bot.updater.dispatcher.add_handler(
            ConversationHandler(
                entry_points=[
                    MessageHandler(
                        Filters.text("✅ Добавить"),
                        tg_bot.see_menu_for_add_crypto,
                    )
                ],
                states={
                    "stage_1": [
                        MessageHandler(
                            Filters.text, tg_bot.add_crypto_in_watchlist
                        )
                    ],
                },
                fallbacks=[],
            )
        )
        tg_bot.updater.dispatcher.add_handler(
            MessageHandler(
                Filters.text("🤑 Цены"), tg_bot.get_price_1_to_14_days
            )
        )
        tg_bot.updater.dispatcher.add_handler(
            MessageHandler(
                Filters.text("📈 График уровней"), tg_bot.see_choice_graph_level
            )
        )
        tg_bot.updater.dispatcher.add_handler(
            MessageHandler(Filters.text("🟢 High"), tg_bot.get_high_level_graph)
        )
        tg_bot.updater.dispatcher.add_handler(
            MessageHandler(Filters.text("🔴 Low"), tg_bot.get_low_level_graph)
        )
        tg_bot.updater.start_polling()
        tg_bot.updater.idle()
    except Exception as error:
        settings.logging.exception(
            f"Ошибка {error} в основном блоке программы", stack_info=True
        )


if __name__ == "__main__":
    main()
