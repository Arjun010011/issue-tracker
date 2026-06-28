from sqlalchemy import create_engine, MetaData
engine = create_engine("sqlite:///mydatabase.db", echo=True)
meta = MetaData()

meta.create_all(engine)


