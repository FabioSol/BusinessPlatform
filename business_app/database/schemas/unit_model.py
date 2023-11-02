from peewee import Model,PrimaryKeyField,FloatField, CharField
from business_app.database import db


class UnitModel(Model):
    id = PrimaryKeyField()
    name = CharField()
    base_rent = FloatField()

    class Meta:
        database = db
