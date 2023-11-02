from peewee import Model, ForeignKeyField, FloatField, CompositeKey, BooleanField
from business_app.database import db
from business_app.database.schemas.month import Month
from business_app.database.schemas.accounting_code import AccountingCode


class TrialBalanceValue(Model):
    month = ForeignKeyField(Month)
    account = ForeignKeyField(AccountingCode)
    initial_balance = FloatField()
    debits = FloatField()
    credits = FloatField()
    final_balance = FloatField()
    is_creditor = BooleanField()


    class Meta:
        database = db
        primary_key = CompositeKey('month', 'account')


