from peewee import Model, PrimaryKeyField, CharField, FloatField, IntegerField, DateField, ForeignKeyField
from business_app.database import db
from business_app.database.schemas.type_of_capital_lease import TypeOfCapitalLease


class CapitalLease(Model):
    id = PrimaryKeyField()
    type_of_capital_lease = ForeignKeyField(TypeOfCapitalLease)
    lender_name = CharField()
    start_date = DateField()
    end_date = DateField()
    amount = FloatField()
    interest_rate = FloatField()
    number_of_payments = IntegerField()
    general_expenses = FloatField(default=0)
    deposit = FloatField(default=0)
    residual = FloatField(default=0)
    initial_payment = FloatField()

    class Meta:
        database = db
