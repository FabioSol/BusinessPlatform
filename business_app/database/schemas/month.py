from peewee import Model, PrimaryKeyField, DateField, FloatField
from business_app.database import db


class Month(Model):
    id = PrimaryKeyField()
    month_date = DateField(unique=True)
    usa_inflation = FloatField()
    mex_inflation = FloatField()
    exchange_rate = FloatField()

    class Meta:
        database = db
