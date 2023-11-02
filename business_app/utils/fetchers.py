import configparser
from business_app import config_path
from datetime import date
import requests

config = configparser.ConfigParser()
config.read(config_path)

fred_api_key = config.get('API', 'fred_api_key')
sie_api_key = config.get('API', 'sie_api_key')

series_exchange = config.get('Series', 'series_exchange')
series_mex_price_index = config.get('Series', 'series_mex_price_index')
series_usa_price_index = config.get('Series', 'series_usa_price_index')


def get_inflation_usa_series(start: date, end: date | None = None):
    # The FRED API URL for inflation rate (CPI) data
    fred_api_url = f'https://api.stlouisfed.org/fred/series/observations?' \
                   f'series_id={series_usa_price_index}&' \
                   f'api_key={fred_api_key}&' \
                   f'file_type=json&' \
                   f'observation_start={start.isoformat()}'
    if end:
        fred_api_url += f"&observation_end={end.isoformat()}"

    # Replace YYYY-MM-DD with the start and end dates for the specific month you want

    # Send the HTTP GET request
    response = requests.get(fred_api_url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract and print the inflation rate for the specific month
        inflation_rate = data['observations']
        return inflation_rate
    else:
        print(f'Request failed with status code {response.status_code}')

print(get_inflation_usa_series(date(2023,1,1)))