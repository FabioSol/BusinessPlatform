from peewee import Model,PrimaryKeyField,ForeignKeyField, CharField
from business_app.database import db
from business_app.database.schemas.client import Client


class Location(Model):
    id = PrimaryKeyField()
    client = ForeignKeyField(Client)
    name = CharField()
    address = CharField(unique=True)

    class Meta:
        database = db
