from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    total_investment: Optional[float] = None
    current_value: Optional[float] = None

class UserLogin(BaseModel):
    email: str
    password: str

class AlertCreate(BaseModel):
    ticker: str
    tp1: Optional[float] = None
    tp2: Optional[float] = None
    tp3: Optional[float] = None
    sl: Optional[float] = None
    percentage_sl: Optional[float] = None
    box_break: Optional[float] = None
    percentage_box_break: Optional[float] = None
    buy_price: Optional[float] = None
    shares: Optional[int] = None

class AlertUpdate(BaseModel):
    ticker: str
    tp1: Optional[float] = None
    tp2: Optional[float] = None
    tp3: Optional[float] = None
    percentage_tp: Optional[float] = None
    sl: Optional[float] = None
    percentage_sl: Optional[float] = None
    box_break: Optional[float] = None
    percentage_box_break: Optional[float] = None
    buy_price: Optional[float] = None
    shares: Optional[int] = None 
    is_sl_hit: Optional[bool] = False
    is_tp1_hit: Optional[bool] = False
    is_tp2_hit: Optional[bool] = False
    is_tp3_hit: Optional[bool] = False
    is_box_break_hit: Optional[bool] = False
    is_percentage_sl_hit: Optional[bool] = False
    is_percentage_tp_hit: Optional[bool] = False
    total_alerts_sent: Optional[int] = 0
