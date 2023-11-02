from peewee import Model, ForeignKeyField, DateField, IntegerField, CompositeKey
from business_app.database import db
from business_app.database.schemas.month import Month
from business_app.database.schemas.client import Client


class SalesPlan(Model):
    month = ForeignKeyField(Month)
    month_date = DateField()
    client = ForeignKeyField(Client)
    full_openings = IntegerField()
    non_recycler_openings = IntegerField()
    recycler_actualizations = IntegerField()

    class Meta:
        database = db
        primary_key = CompositeKey('month', 'month_date', 'client')
