from sqlalchemy import create_engine, Column, Integer, String, VARCHAR
from sqlalchemy.orm import declarative_base

#SQL Database setup
DATABASE_URI = 'sqlite:///main.db'
engine = create_engine(DATABASE_URI)
Base = declarative_base()

class Cache(Base): 
    __tablename__="userMessageCache"
    origin = Column(Integer, primary_key=True)
    activeSessions = Column(String, nullable=True)
    globalChatTask = Column(String, nullable=True)
    activeModel = Column(VARCHAR(1), nullable=True)

class Persona(Base):
    __tablename__="personalities"
    id = Column(Integer, primary_key=True)
    origin = Column(Integer)
    name = Column(String)
    profilePicture = Column(String)
    personality = Column(String)

Base.metadata.create_all(engine)