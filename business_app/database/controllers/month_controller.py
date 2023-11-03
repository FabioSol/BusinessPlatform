from business_app.database import db
from business_app.database.schemas import Month
from datetime import date
from typing import Union
from peewee import DoesNotExist, IntegrityError
from business_app.utils.decorators import tabulate
from business_app.utils.fetchers import get_exchange_rate_series, get_mex_series, get_usa_series


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

    def __repr__(self):
        return f"Month: {self.month_date}"

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

    @classmethod
    def update(cls,
               month_date: date,
               usa_price_index: float,
               mex_price_index: float,
               exchange_rate: float):
        try:
            mnth = Month.get(Month.month_date == month_date)
            print("updating")
            mnth.usa_price_index = usa_price_index
            mnth.mex_price_index = mex_price_index
            mnth.exchange_rate = exchange_rate

            mnth.save()
            return ObjMonth.get(month_date)

        except DoesNotExist:
            raise ValueError("Month does not exist")

    @classmethod
    def auto_create(cls, start: date, end: date = None, overwrite=False):
        usa_series = get_usa_series(start, end)
        mex_series = get_mex_series(start, end)
        exchange_series = get_exchange_rate_series(start, end)
        combined_data = [
            (e_date, usa_value, mex_value, exchange_rate)
            for usa_date, usa_value in usa_series
            for mex_date, mex_value in mex_series
            for e_date, exchange_rate in exchange_series
            if usa_date == mex_date == e_date
        ]
        months = []
        for month_values in combined_data:
            mnth = None
            try:
                response = Month.create(month_date=month_values[0],
                                        usa_price_index=month_values[1],
                                        mex_price_index=month_values[2],
                                        exchange_rate=month_values[3])
                mnth = ObjMonth(month_id=response.id,
                                month_date=response.month_date,
                                usa_price_index=response.usa_price_index,
                                mex_price_index=response.mex_price_index,
                                exchange_rate=response.exchange_rate)

            except IntegrityError:
                if overwrite:
                    mnth = ObjMonth.update(*month_values)
                else:
                    pass

            months += [mnth]

        return months

    @staticmethod
    @tabulate
    def get_all():
        q = "SELECT * FROM Month"
        return db.execute_sql(q)

print(ObjMonth.get_all())
