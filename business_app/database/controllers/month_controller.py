from business_app.database import db
from business_app.database.schemas import Month
from datetime import date
from typing import Union
from peewee import DoesNotExist, IntegrityError
from business_app.utils.decorators import tabulate

class ObjMonth:
    def __init__(self,
                 month_id: int,
                 month_date: date,
                 usa_price_index: float,
                 mex_price_index: float,
                 exchange_rate: float):
        self.month_id = month_id
        self.month_date = month_date
        self.usa_price_index = usa_price_index
        self.mex_price_index = mex_price_index
        self.exchange_rate = exchange_rate

    def __str__(self):
        return f"Month: {self.month_id}\n" \
               f"   Date:         {self.month_date}\n" \
               f"   USA price_index: {self.usa_price_index:9}\n" \
               f"   MEX price_index: {self.mex_price_index:9}\n" \
               f"   Exchange rate: {self.exchange_rate:9}"
    @classmethod
    def get(cls, month: Union[int, date]):
        if isinstance(month, int):
            try:
                response = Month.get(Month.id == month)
            except DoesNotExist:
                raise ValueError("That month does not exist")

        elif isinstance(month, date):
            try:
                response = Month.get(Month.month_date == month)
            except DoesNotExist:
                raise ValueError("That month does not exist")

        else:
            raise TypeError(f"Not supported type {type(month)}")
        return ObjMonth(month_id=response.id,
                        month_date=response.month_date,
                        usa_price_index=response.usa_price_index,
                        mex_price_index=response.mex_price_index,
                        exchange_rate=response.exchange_rate)

    @classmethod
    def create(cls,
               month_date: date,
               usa_price_index: float,
               mex_price_index: float,
               exchange_rate: float):
        try:
            response = Month.create(month_date=month_date,
                                    usa_price_index=usa_price_index,
                                    mex_price_index=mex_price_index,
                                    exchange_rate=exchange_rate)
            return ObjMonth(month_id=response.id,
                        month_date=response.month_date,
                        usa_price_index=response.usa_price_index,
                        mex_price_index=response.mex_price_index,
                        exchange_rate=response.exchange_rate)
        except IntegrityError:
            raise ValueError("Month already exist")

    @staticmethod
    @tabulate
    def get_all():
        q = "SELECT * FROM Month"
        return db.execute_sql(q)








d=date(2022,1,1)
d2 =date(2022,2,1)
print(ObjMonth.get_all())

#print(ObjMonth.create(d2,1,1,1))