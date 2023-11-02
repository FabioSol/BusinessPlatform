from peewee import Model, PrimaryKeyField, CharField
from business_app.database import db


class AccountingCode(Model):
    id = PrimaryKeyField()
    account_number = CharField()
    account_name = CharField()
    account_type = CharField(default="Forecast")
    account_model = CharField(default="Mean")

    class Meta:
        database = db
