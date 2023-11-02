from peewee import Model, ForeignKeyField, IntegerField, CompositeKey
from business_app.database import db
from business_app.database.schemas.client import Client
from business_app.database.schemas.competitor import Competitor


class CompetitorStock(Model):
    client = ForeignKeyField(Client)
    competitor = ForeignKeyField(Competitor)
    units = IntegerField()

    class Meta:
        database = db
        primary_key = CompositeKey("client", "competitor")
