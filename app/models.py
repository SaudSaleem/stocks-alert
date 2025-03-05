from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    password = Column(String)
    token = Column(String, nullable=True)
    total_investment = Column(Float, default=0)
    current_value = Column(Float, default=0)

class Alert(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    ticker = Column(String, index=True)
    tp1 = Column(Float, nullable=True)
    tp2 = Column(Float, nullable=True)
    tp3 = Column(Float, nullable=True)
    percentage_tp = Column(Float, nullable=True)
    sl = Column(Float, nullable=True)
    percentage_sl = Column(Float, nullable=True)
    trailing_stop_percentage = Column(Float, nullable=True)
    highest_price = Column(Float, nullable=True)
    box_break = Column(Float, nullable=True)
    percentage_box_break = Column(Float, nullable=True)
    buy_price = Column(Float, nullable=True)
    shares = Column(Integer, nullable=True)
    current_price = Column(Float, nullable=True)
    change_percentage = Column(Float, nullable=True)
    is_sl_hit = Column(Boolean, default=False)
    is_tp1_hit = Column(Boolean, default=False)
    is_tp2_hit = Column(Boolean, default=False)
    is_tp3_hit = Column(Boolean, default=False)
    is_box_break_hit = Column(Boolean, default=False)
    is_percentage_sl_hit = Column(Boolean, default=False)
    is_percentage_tp_hit = Column(Boolean, default=False)
    is_trailing_stop_hit = Column(Boolean, default=False)
    total_alerts_sent = Column(Integer, default=0)
    date_added = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    date_modified = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)) 