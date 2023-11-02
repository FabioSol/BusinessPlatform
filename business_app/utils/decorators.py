import pandas as pd

def tabulate(func):
    def wrapper(*args,**kwargs):
        cursor = func(*args, **kwargs)
        columns=[tup[0] for tup in cursor.description]
        data=cursor.fetchall()
        return pd.DataFrame(data=data,columns=columns)
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
