from peewee import Model, ForeignKeyField, FloatField, DateField, CompositeKey
from business_app.database import db
from business_app.database.schemas.month import Month


class ForecastedPremise(Model):

    month = ForeignKeyField(Month)
    month_date = DateField()
    usa_inflation = FloatField()
    mex_inflation = FloatField()
    exchange_rate = FloatField()

    class Meta:
        database = db
        primary_key = CompositeKey('month', 'month_date')





