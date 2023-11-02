from peewee import Model, ForeignKeyField, DateField, FloatField, CompositeKey
from business_app.database import db
from business_app.database.schemas.month import Month
from business_app.database.schemas.accounting_code import AccountingCode


class TrialBalanceProjectedValue(Model):
    month = ForeignKeyField(Month)
    month_date = DateField()
    account = ForeignKeyField(AccountingCode)
    initial_balance = FloatField()
    debits = FloatField()
    credits = FloatField()
    final_balance = FloatField()

    class Meta:
        database = db
        primary_key = CompositeKey('month','month_date', 'account')
