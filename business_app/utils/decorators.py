import pandas as pd
import requests
from business_app import SIE_API
from datetime import date, datetime
def tabulate(func):
    def wrapper(*args,**kwargs):
        cursor = func(*args, **kwargs)
        columns=[tup[0] for tup in cursor.description]
        data=cursor.fetchall()
        df = pd.DataFrame(data=data,columns=columns)
        if 'id' in columns:
            df.set_index('id', inplace=True)
        return df
    return wrapper

def dictionary(func):
    def wrapper(*args,**kwargs):
        cursor = func(*args, **kwargs)
        data=cursor.fetchall()
        try:
            if len(data[0])==2:
                return {i[0]:i[1] for i in data}
            else:
                return {i[0]:i[1:] for i in data}
        except Exception as e:
            print(f"Error: {e}")
            return {}
    return wrapper

def listing(func):
    def wrapper(*args,**kwargs):
        cursor = func(*args, **kwargs)
        data=cursor.fetchall()
        try:
            if len(data[0])==1:
                return [i[0] for i in data]
            else:
                return [i for i in data]
        except Exception as e:
            print(f"Error: {e}")
            return []
    return wrapper

def banxico_handle_and_parse(func):
    def wrapper(start, end=None):

        headers = {"Bmx-Token": SIE_API}
        url = func(start, end)

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            tup_res = [(datetime.strptime(dato['fecha'], '%d/%m/%Y').date(), dato['dato']) for dato in
                       data['bmx'].get('series')[0].get('datos')]
            return tup_res
        else:
            print(f'Request failed with status code {response.status_code}')

    return wrapper


def fred_handle_and_parse(func):
    def wrapper(start, end=None):
        url = func(start, end)
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            tup_res = [(date.fromisoformat(obs['date']), obs['value']) for obs in data['observations']]
            return tup_res
        else:
            print(f'Request failed with status code {response.status_code}')

    return wrapper