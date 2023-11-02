from peewee import Model, PrimaryKeyField, DateField, FloatField
from business_app.database import db


class Month(Model):
    id = PrimaryKeyField()
    month_date = DateField(unique=True)
    usa_price_index = FloatField()
    mex_price_index = FloatField()
    exchange_rate = FloatField()

    class Meta:
        database = db
