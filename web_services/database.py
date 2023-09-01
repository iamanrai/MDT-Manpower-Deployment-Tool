from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

eng = create_engine("sqlite:///userManagement.db",echo=True)

Base = declarative_base()


Session = sessionmaker(bind=eng, autoflush=True)

# from main import db
# db.create_all()