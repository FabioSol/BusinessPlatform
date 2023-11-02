from peewee import Model, ForeignKeyField, CompositeKey
from business_app.database import db
from business_app.database.schemas.capital_lease import CapitalLease
from business_app.database.schemas.unit import Unit


class CapitalLeaseUnit(Model):
    unit = ForeignKeyField(Unit)
    capital_lease = ForeignKeyField(CapitalLease)

    class Meta:
        database = db
        primary_key = CompositeKey('unit', 'capital_lease')
