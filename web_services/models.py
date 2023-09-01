from database import Base
from sqlalchemy import Column, ForeignKey, Float
from sqlalchemy.orm import relationship, sessionmaker,joinedload
from sqlalchemy.dialects.sqlite import INTEGER, VARCHAR, JSON, DATETIME
from flask_login import UserMixin

class User(Base,UserMixin):
    __tablename__ = "user"
    userid = Column(VARCHAR(50), primary_key = True, index = True)
    name = Column(VARCHAR(256), nullable = False)
    password = Column(VARCHAR(256), nullable = False)
    rights = Column(INTEGER, default=2,nullable=False)
    location = Column(VARCHAR(256))

    def as_dict(self):
        return {i.name : getattr(self, i.name) 
                         for i in self.__table__.column}

    # user_locations = relationship('Location', back_populates = "locations_user")
    
class AOP(Base):
    __tablename__ = "aop"
    loc_code = Column(INTEGER,primary_key=True, nullable=False)
    loc_name = Column(VARCHAR(50), nullable=False)
    zone = Column(VARCHAR(50), nullable=False)
    gm = Column(VARCHAR(50), nullable=False)
    aop_count = Column(INTEGER, nullable=False)
    
class DensityMix(Base):
    __tablename__ ="densitymix"
    loc_name = Column(VARCHAR(50),primary_key=True, nullable=False)
    uhd = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    medium = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    
class ActiveHeadCount(Base):
    __tablename__ = "activeheadcount"
    loc_name = Column(VARCHAR(50),primary_key=True, nullable=False)
    EFLEX = Column(INTEGER, nullable=True)
    EKARTOthers = Column(INTEGER, nullable=True)
    EKARTWM = Column(INTEGER, nullable=True)
    KIRANA = Column(INTEGER, nullable=True)
    LMA = Column(INTEGER, nullable=True)
    CB = Column(INTEGER, nullable=True)
    RFK = Column(INTEGER, nullable=True)
    TRUEFLEXRegular = Column(INTEGER, nullable=True)
    TrueflexLCM = Column(INTEGER, nullable=True)
    TrueflexUHD = Column(INTEGER, nullable=True)

class ActiveHeadCountBifrication(Base):
    __tablename__ ="activeheadcountbifrication"
    loc_name = Column(VARCHAR(50),primary_key=True, nullable=False)
    uhd = Column(Float)
    high = Column(Float)
    medium = Column(Float)
    low = Column(Float)

