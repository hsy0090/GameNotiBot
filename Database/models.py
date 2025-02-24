
# Database/models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    confirmed = Column(Boolean, default=False)
    prices = relationship("Price", back_populates="game")

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)
    game = relationship("Game", back_populates="prices")

# Database setup
engine = create_engine("sqlite:///games.db")
Session = sessionmaker(bind=engine)
session = Session()

# Create tables
Base.metadata.create_all(engine)


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///games.db")
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)


# Define the database
Base = declarative_base()
engine = create_engine("sqlite:///bot_data.db")  # SQLite database file
Session = sessionmaker(bind=engine)
session = Session()

class BotConfig(Base):
    __tablename__ = "bot_config"
    
    id = Column(Integer, primary_key=True)
    free_games_channel = Column(Integer, nullable=True)  # Store channel ID
    free_games_time = Column(String, default="12:00")  # Store time in "HH:MM" format

# Create the table if it doesn't exist
Base.metadata.create_all(engine)
