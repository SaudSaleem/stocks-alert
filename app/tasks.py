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
            return current_price
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
                # Check alert conditions
                print('calculate_percentage_change', calculate_percentage_change(current_price, alert.buy_price))
                alert.change_percentage = calculate_percentage_change(current_price, alert.buy_price)
                print('percentage change of', alert.ticker, 'is: ', alert.change_percentage)
                alert.current_price = current_price
                print('current price of', alert.ticker, ' after update is: ', alert.current_price)
                db.commit()
                print('alert after commit', alert.change_percentage)
                if alert.sl and current_price <= alert.sl:
                    send_email("Stop Loss Alert", f"The stock {alert.ticker} has hit the stop loss price. Current price: {current_price}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.sl = None
                    alert.is_sl_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.tp1 and current_price >= alert.tp1:
                    send_email("Take Profit Alert", f"The stock {alert.ticker} has hit the take profit level 1. Current price: {current_price}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.tp1 = None
                    alert.is_tp1_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.tp2 and current_price >= alert.tp2:
                    send_email("Take Profit Alert", f"The stock {alert.ticker} has hit the take profit level 2. Current price: {current_price}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.tp2 = None
                    alert.is_tp2_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.tp3 and current_price >= alert.tp3:
                    send_email("Take Profit Alert", f"The stock {alert.ticker} has hit the take profit level 3. Current price: {current_price}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.tp3 = None
                    alert.is_tp3_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.box_break and current_price >= alert.box_break:
                    send_email("Box Break Alert", f"The stock {alert.ticker} has hit the box break price. Current price: {current_price}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.box_break = None
                    alert.is_box_break_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.percentage_tp and alert.change_percentage >= alert.percentage_tp:
                    send_email("Take Profit Alert for percentage", f"The stock {alert.ticker} has hit the take profit level. Current price: {current_price}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.percentage_tp = None
                    alert.is_percentage_tp_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                elif alert.percentage_sl and alert.change_percentage <= alert.percentage_sl:
                    send_email("Stop Loss Alert for percentage", f"The stock {alert.ticker} has hit the stop loss level. Current price: {current_price}", user.email, MAIL_FROM, MAIL_PASSWORD)
                    alert.percentage_sl = None
                    alert.is_percentage_sl_hit = True
                    alert.total_alerts_sent = alert.total_alerts_sent + 1
                    db.commit()
                # Add more conditions for tp2, tp3, and box_break
    except Exception as e:
        db.rollback()
        print(f"Error in check_alerts: {e}")
    finally:
        db.close()

# Scheduler setup
# def start_scheduler():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(check_alerts, 'interval', minutes=1)
#     scheduler.start() 