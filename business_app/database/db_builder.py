from business_app.database import db_path, db
from business_app.database.schemas import *
import os

def create_db(path: str):
    if not os.path.isfile(path):
        model_classes = [Month, AccountingCode, TrialBalanceValue, TrialBalanceProjectedValue, ForecastedPremise,
                         Client, Competitor, CompetitorStock, UnitsLease, Substitution, SalesPlan, SubstitutionPlan,
                         TypeOfCapitalLease, CapitalLease, Payment, UnitModel, Location, Unit, CapitalLeaseUnit,
                         UnitsLeaseUnit]
        db.create_tables(model_classes)

if __name__ == '__main__':
    create_db(db_path)
