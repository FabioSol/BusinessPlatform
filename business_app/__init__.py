import os
import configparser

config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config.ini"

config = configparser.ConfigParser()
config.read(config_path)


try:
    from config import apikeys
    FRED_API = apikeys.get("FRED")
    SIE_API = apikeys.get("SIE")

except ModuleNotFoundError:

    FRED_API = config.get('API', 'fred_api_key')
    SIE_API = config.get('API', 'sie_api_key')

SERIES_EXCHANGE = config.get('Series', 'series_exchange')
SERIES_MEX_PRICE_INDEX = config.get('Series', 'series_mex_price_index')
SERIES_USA_PRICE_INDEX = config.get('Series', 'series_usa_price_index')

