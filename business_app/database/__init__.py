import os
from peewee import SqliteDatabase
db_path = os.path.dirname(os.path.abspath(__file__)) + "/business.db"
db = SqliteDatabase(db_path, timeout=10)
