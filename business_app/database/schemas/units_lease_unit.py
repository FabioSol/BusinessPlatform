from peewee import Model, ForeignKeyField, CompositeKey
from business_app.database import db
from business_app.database.schemas.units_lease import UnitsLease
from business_app.database.schemas.unit import Unit


class UnitsLeaseUnit(Model):
    unit = ForeignKeyField(Unit)
    month = ForeignKeyField(UnitsLease, field='month')
    client = ForeignKeyField(UnitsLease, field='client')


    class Meta:
        database = db
        primary_key = CompositeKey('unit', 'month','client')
        indexes = (
            (('month', 'client'), True),  # Unique composite index for the foreign key
        )