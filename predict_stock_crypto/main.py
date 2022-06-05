
from config import settings, date_time, client_settings
from graph import graphics_stock
from messaging import telegram_bot
from parse import parse

all_symbol = settings.SYMBOL_DATA_LIST
country = client_settings.country
dict_date = date_time.set_current_to_from_date()
stock_or_crypto = client_settings.is_crypto_parse

def main():
    for symbol in all_symbol:
        df = parse.get_historical_data(
            symbol=symbol[0],
            from_date=dict_date['old-date'],
            today_date=dict_date['today'],
            is_crypto=stock_or_crypto,
            country=country)
        img_name = graphics_stock.stock_to_graph(
            df=df,
            from_date=dict_date['old-date'],
            today_date=dict_date['today'],
            stock=symbol[0],
            function='EMA')
        telegram_bot.send_photo(img_name)
        
if __name__ == '__main__':
    main()