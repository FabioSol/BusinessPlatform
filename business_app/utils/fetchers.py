from business_app import SERIES_USA_PRICE_INDEX, SERIES_MEX_PRICE_INDEX, SERIES_EXCHANGE, FRED_API
from datetime import date
from business_app.utils.decorators import fred_handle_and_parse,banxico_handle_and_parse

@fred_handle_and_parse
def get_usa_series(start: date, end: date | None = None):
    fred_api_url = f'https://api.stlouisfed.org/fred/series/observations?' \
                   f'series_id={SERIES_USA_PRICE_INDEX}&' \
                   f'api_key={FRED_API}&' \
                   f'file_type=json&' \
                   f'observation_start={start.isoformat()}'
    if end:
        fred_api_url += f"&observation_end={end.isoformat()}"
    else:
        fred_api_url += f"&observation_end={start.isoformat()}"
    return fred_api_url


@banxico_handle_and_parse
def get_mex_series(start: date, end: date | None = None):
    sie_api_url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{SERIES_MEX_PRICE_INDEX}/datos/{start.isoformat()}"
    if end:
        sie_api_url += f"/{end.isoformat()}"
    else:
        sie_api_url += f"/{start.isoformat()}"
    return sie_api_url


@banxico_handle_and_parse
def get_exchange_rate_series(start: date, end: date | None = None):
    sie_api_url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{SERIES_EXCHANGE}/datos/{start.isoformat()}"
    if end:
        sie_api_url += f"/{end.isoformat()}"
    else:
        sie_api_url += f"/{start.isoformat()}"
    return sie_api_url

