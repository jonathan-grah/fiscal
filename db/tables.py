from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    Text,
    ForeignKey,
    MetaData,
    Table
)

import configparser

config = configparser.ConfigParser()
config.read("config.ini")

db_path = config["database"]["path"]

engine = create_engine(f"sqlite:///{db_path}")

metadata = MetaData()

country = Table(
    'countries',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Text),
    Column('iso', Text),
    Column('knoemaKey', Integer),
    Column('knoemaRegionId', Text)
)

# The type of indicator - for example GDP growth annually
indicatorType = Table(
    'indicatorTypes',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('knoemaKey', Integer, unique=True),
    Column('name', Text),
    Column('description', Text)
)

# Stores actual values of economic indicators e.g. a GDP growth of 3% in 2019
indicator = Table(
    'indicators',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('countryRegionId', Integer, ForeignKey('countries.knoemaRegionId')),
    Column('value', Float),
    Column('indicatorTypeId', Integer, ForeignKey('indicatorTypes.id'))
)


# TODO: should only happen if table doesn't exist/program is bootstrapping
def create():
    if not (engine.dialect.has_table(engine, 'countries')):
        country.create(bind=engine)

    if not (engine.dialect.has_table(engine, 'indicatorTypes')):
        indicatorType.create(bind=engine)

    if not(engine.dialect.has_table(engine, 'indicators')):
        indicator.create(bind=engine)