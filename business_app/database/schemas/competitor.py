from peewee import Model, PrimaryKeyField, CharField
from business_app.database import db


class Competitor(Model):
    id = PrimaryKeyField()
    competitor_name = CharField(unique=True)

    class Meta:
        database = db
