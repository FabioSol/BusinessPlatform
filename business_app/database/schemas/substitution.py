from peewee import Model, ForeignKeyField, IntegerField, CompositeKey
from business_app.database import db
from business_app.database.schemas.units_lease import UnitsLease
from business_app.database.schemas.competitor import Competitor


class Substitution(Model):
    month = ForeignKeyField(UnitsLease, field='month')
    client = ForeignKeyField(UnitsLease, field='client')
    competitor = ForeignKeyField(Competitor)
    substitutions = IntegerField()

    class Meta:
        database = db
        primary_key = CompositeKey('month', 'client','competitor')


