from business_app.database import db_path
from business_app.database.db_builder import create_db
from business_app.database.controllers.month_controller import ObjMonth
from datetime import date

def create_months():
    start = date(2020, 1, 1)
    end = date.today()
    ObjMonth.auto_create(start,end)


if __name__ == '__main__':
    create_db(db_path)
    create_months()
