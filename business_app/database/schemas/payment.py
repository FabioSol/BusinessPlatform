from peewee import Model, FloatField, IntegerField, DateField, ForeignKeyField, CompositeKey
from business_app.database import db
from business_app.database.schemas.capital_lease import CapitalLease


class Payment(Model):
    capital_lease = ForeignKeyField(CapitalLease)
    number_of_payment = IntegerField()
    date = DateField()
    amount = FloatField()

    class Meta:
        database = db
        primary_key = CompositeKey("capital_lease","number_of_payment")
