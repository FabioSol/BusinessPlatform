from peewee import Model, PrimaryKeyField, CharField
from business_app.database import db


class TypeOfCapitalLease(Model):
    id = PrimaryKeyField()
    name = CharField(unique=True)

    class Meta:
        database = db

