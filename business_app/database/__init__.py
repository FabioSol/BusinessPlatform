import os
from peewee import SqliteDatabase
db_path = os.getcwd() + "/business.db"
db = SqliteDatabase(db_path, timeout=10)
