from peewee import Model,PrimaryKeyField,BooleanField, ForeignKeyField
from business_app.database import db
from business_app.database.schemas.unit_model import UnitModel
from business_app.database.schemas.location import Location


class Unit(Model):
    id = PrimaryKeyField()
    model = ForeignKeyField(UnitModel)
    address = ForeignKeyField(Location)
    active = BooleanField()

    class Meta:
        database = db