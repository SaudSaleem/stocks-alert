from apscheduler.schedulers.background import BackgroundScheduler
from .crud import get_alerts_by_user_id, update_alert
from .email_utils import send_email
from .database import SessionLocal
from . import models
from psx import stocks, tickers
from datetime import date, timedelta
from dotenv import load_dotenv
import os
import json
import traceback
load_dotenv()

MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_FROM = os.getenv('MAIL_FROM')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_STARTTLS = os.getenv('MAIL_STARTTLS')

def get_ticker_by_symbol(ticker: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tickers_path = os.path.join(script_dir, "data", "latest_stock_price.json")
    with open(tickers_path, "r") as f:
        data = json.load(f)
    for item in data:
        if item['symbol'] == ticker:
            return item
    return None

def fetch_all_tickers():
    tickersDf = tickers()
    # print('from tasks',tickersDf.loc[0]['symbol'])
    return [{'symbol': ticker['symbol'], 'name': ticker['name']} for _, ticker in tickersDf.iterrows()]

def calculate_percentage_change(current_price, buy_price):
    try:
        if(buy_price == None or buy_price == 0):
            return None
        return round(((current_price - buy_price) / buy_price) * 100, 2)
    except Exception as e:
        print(f"Error in calculate_percentage_change: {e}")
        return None

# Function to fetch stock price
# def fetch_stock_price(stock_name: str):
#     try:
#         start_date = date.today() - timedelta(days=1)
#         end_date = date.today()
#         data = stocks(stock_name, start=start_date, end=end_date)
#         latest_data = data.iloc[-1]  # Get the latest available data
#         return latest_data['Close']
#     except Exception as e:
#         print(f"Error fetching stock price for {stock_name}: {e}")
#         return None

def fetch_stock_price(stock_name: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tickers_path = os.path.join(script_dir, "data", "latest_stock_price.json")
    with open(tickers_path, "r") as f:
        data = json.load(f)
    for item in data:
        if item['symbol'] == stock_name:
            return item['current']
    return None

# Function to check alerts
def check_alerts():
    db = SessionLocal()
    try:
        users = db.query(models.User).all()
        for user in users:
            alerts = get_alerts_by_user_id(db, user.id)
            print('in check_alerts method: alerts', alerts)
            for alert in alerts:
                current_price = float(fetch_stock_price(alert.ticker))

                print('current price of', alert.ticker, 'is: ', current_price)
                if current_price is None:
                    continue
                
                # Update highest price for trailing stop if needed
                if alert.trailing_stop_percentage and (alert.highest_price is None or current_price > alert.highest_price):
                    alert.highest_price = current_price
                    db.commit()
                
                # Check alert conditions
                alert.change_percentage = calculate_percentage_change(current_price, alert.buy_price)
                alert.current_price = current_price
                db.commit()
                # Check trailing stop condition
                if (alert.is_trailing_stop_hit == False and 
                    alert.trailing_stop_percentage and 
                    alert.highest_price and 
                    current_price < alert.highest_price * (1 - alert.trailing_stop_percentage / 100)):
                    
                    drop_percentage = round(((alert.highest_price - current_price) / alert.highest_price) * 100, 2)
                    send_email(
                        "Trailing Stop Alert", 
                        f"Trailing Stop hit. The stock {alert.ticker} has dropped {drop_percentage}% from its highest price of {alert.highest_price}. Current price: {current_price}, Notes: {alert.notes}", 
                        user.email, 
                        MAIL_FROM, 
                        MAIL_PASSWORD
                    )
                    alert.is_trailing_stop_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                
                # Check dip buy condition
                elif alert.is_dip_buy_hit == False and alert.dip_buy and current_price <= alert.dip_buy:
                    send_email(
                        "Dip Buy Alert", 
                        f"The stock {alert.ticker} has reached or fallen below your dip buy price of {alert.dip_buy}. Current price: {current_price}, Notes: {alert.notes}", 
                        user.email, 
                        MAIL_FROM, 
                        MAIL_PASSWORD
                    )
                    alert.is_dip_buy_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                
                # Existing alert conditions
                elif alert.is_sl_hit == False and alert.sl and current_price <= alert.sl:
                    send_email("Stop Loss Alert", f"The stock {alert.ticker} has hit the stop loss price: {alert.sl}. Current price: {current_price}, Notes: {alert.notes}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.is_sl_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.is_tp1_hit == False and alert.tp1 and current_price >= alert.tp1:
                    send_email("Take Profit Alert", f"The stock {alert.ticker} has hit the take profit level 1: {alert.tp1}. Stop loss price is set to buy price {alert.buy_price}. Current price: {current_price}, Notes: {alert.notes}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.sl = alert.buy_price
                    alert.is_sl_hit = False
                    alert.is_tp1_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.is_tp2_hit == False and alert.tp2 and current_price >= alert.tp2:
                    send_email("Take Profit Alert", f"The stock {alert.ticker} has hit the take profit level 2: {alert.tp2}. Stop loss price is set to take profit level 1 {alert.tp1}. Current price: {current_price}, Notes: {alert.notes}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.sl = alert.tp1
                    alert.is_sl_hit = False
                    alert.is_tp2_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.is_tp3_hit == False and alert.tp3 and current_price >= alert.tp3:
                    send_email("Take Profit Alert", f"The stock {alert.ticker} has hit the take profit level 3: {alert.tp3}. Stop loss price is set to take profit level 2 {alert.tp2}. Current price: {current_price}, Notes: {alert.notes}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.sl = alert.tp2
                    alert.is_sl_hit = False
                    alert.is_tp3_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.is_box_break_hit == False and alert.box_break and current_price >= alert.box_break:
                    send_email("Box Break Alert", f"The stock {alert.ticker} has hit the box break price {alert.box_break}. Current price: {current_price}, Notes: {alert.notes}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.is_box_break_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.is_percentage_tp_hit == False and alert.percentage_tp and alert.change_percentage >= alert.percentage_tp:
                    send_email("Take Profit Alert for percentage", f"The stock {alert.ticker} has hit the take profit level {alert.percentage_tp}. Current price: {current_price}, Notes: {alert.notes}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.is_percentage_tp_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.is_percentage_sl_hit == False and alert.percentage_sl and alert.change_percentage <= -abs(alert.percentage_sl):
                    send_email("Stop Loss Alert for percentage", f"The stock {alert.ticker} has hit the percentage stop loss level {alert.percentage_sl}. Current price: {current_price}, Notes: {alert.notes}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.is_percentage_sl_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                # Add more conditions for tp2, tp3, and box_break
    except Exception as e:
        db.rollback()
        print(f"Error in check_alerts: {e}")
        traceback.print_exc() 
    finally:
        db.close()

# Scheduler setup
# def start_scheduler():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(check_alerts, 'interval', minutes=1)
#     scheduler.start() 