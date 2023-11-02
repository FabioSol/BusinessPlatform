from peewee import Model, ForeignKeyField, IntegerField, CompositeKey
from business_app.database import db
from business_app.database.schemas.sales_plan import SalesPlan
from business_app.database.schemas.competitor import Competitor


class SubstitutionPlan(Model):
    month = ForeignKeyField(SalesPlan, field='month')
    month_date = ForeignKeyField(SalesPlan, field='month')
    client = ForeignKeyField(SalesPlan, field='client')

    competitor = ForeignKeyField(Competitor)
    substitutions = IntegerField()

    class Meta:
        database = db
        primary_key = CompositeKey('month','month_date', 'client', 'competitor')
