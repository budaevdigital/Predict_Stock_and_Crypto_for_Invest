import investpy
import pandas as pd

def get_historical_data(symbol: str, 
                        from_date: str, 
                        today_date: str, 
                        is_crypto: bool,
                        country: str) -> pd.DataFrame:
    match is_crypto:
        case True:
            try:
                df = investpy.get_crypto_historical_data(
                    crypto=symbol,
                    from_date=from_date,
                    to_date=today_date)
                return df
            except Exception as error:
                print(error)
                df = None
                return df
        case False:
            try:
                df = investpy.get_stock_historical_data(
                    stock=symbol,
                    country= country,
                    from_date=from_date,
                    to_date=today_date)
                return df                    
            except Exception as error:
                print(error)
                df = None
                return df
