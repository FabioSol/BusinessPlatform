import configparser
from business_app import config_path
config = configparser.ConfigParser()
config.read(config_path)

fred_api_key = config.get('API','fred_api_key')
sie_api_key = config.get('API','sie_api_key')

series_exchange = config.get('Series','series_exchange')
series_mex_price_index = config.get('Series','series_mex_price_index')
series_usa_price_index = config.get('Series','series_usa_price_index')


