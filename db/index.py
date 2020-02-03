from sqlalchemy import (
	create_engine,
	Column,
	Integer,
	Text,
	MetaData,
	Table
)

import configparser

config = configparser.ConfigParser()
config.read("config.ini")

db_path = config["database"]["path"]

engine = create_engine(f"sqlite:///{db_path}")

metadata = MetaData()

countries = Table(
    'countries', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Text),
)

try:
	countries.create(bind=engine)
except Exception as e:
	print("Error", e)