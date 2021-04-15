'''
Define database models and initialize connection.
'''

from sqlalchemy import (
    create_engine,
    Boolean,
    Column,
    DateTime,
    Integer,
    ForeignKey,
    MetaData,
    String,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

'''
Define tables
'''

Base = declarative_base()

class Guild(Base):
    __tablename__ = 'guilds'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    money = Column(Integer)
    
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=True)
    guild = relationship('Guild', foreign_keys=[guild_id])
    

class GuildInteraction(Base):
    __tablename__ = 'guild_interactions'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # if join=False, the player is leaving the guild
    join = Column(Boolean)
    
    player_id = Column(Integer, ForeignKey('players.id'))
    player = relationship('Player', foreign_keys=[player_id])
    
    guild_id = Column(Integer, ForeignKey('guilds.id'))
    guild = relationship('Guild', foreign_keys=[guild_id])
    

class Sword(Base):
    __tablename__ = 'swords'
    id = Column(Integer, primary_key=True)
    cost = Column(Integer)
    
    player_id = Column(Integer, ForeignKey('players.id'), nullable=True)
    player = relationship('Player', foreign_keys=[player_id])
     

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    sword_id = Column(Integer, ForeignKey('swords.id'))
    sword = relationship('Sword', foreign_keys=[sword_id])
    
    buyer_id = Column(Integer, ForeignKey('players.id'))
    buyer = relationship('Player', foreign_keys=[buyer_id])
    
    # if sword is bought from market/NPC, seller_id=None
    seller_id = Column(Integer, ForeignKey('players.id'), nullable=True)
    seller = relationship('Player', foreign_keys=[seller_id]) 
    

'''
Start the session
'''

engine = create_engine('sqlite:////sqllight.db')
# metadata.create_all(engine)
Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
