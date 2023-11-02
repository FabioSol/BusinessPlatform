from peewee import Model, PrimaryKeyField, CharField, IntegerField
from business_app.database import db


class Client(Model):
    id = PrimaryKeyField()
    client_name = CharField(unique=True)
    double_inventory = IntegerField()
    simple_inventory = IntegerField()

    class Meta:
        database = db
