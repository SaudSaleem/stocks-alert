import requests
from psx import stocks, tickers
from datetime import date
BASE_URL = "http://localhost:8000"
from app.tasks import check_alerts, fetch_stock_price

def get_stock_price(ticker):
    fetch_stock_price(ticker)

def test_check_alerts():
    check_alerts()

def test_register_user():
    response = requests.post(f"{BASE_URL}/register", json={
        "name": "Saud Saleem",
        "email": "sauddsaleem+test@gmail.com",
        "password": "heheshampoo",
        "phone": "03086950078"
    })
    print("Register User:", response.status_code, response.json())

def test_login():
    response = requests.post(f"{BASE_URL}/login/json", json={
        "email": "sauddsaleem+test@gmail.com",
        "password": "heheshampoo"
    })
    print("Login:", response.status_code, response.json())

def test_create_alert():
    response = requests.post(f"{BASE_URL}/alert?user_id=1", json={
        "ticker": "MARI",
        "tp1": 570,
        "tp2": 580,
        "tp3": 590,
        "sl": 560,
        "box_break": 550,
        "buy_price": 565,
        "shares": 10
    })
    print("Create Alert:", response.status_code, response.json())

def test_get_alerts():
    response = requests.get(f"{BASE_URL}/alerts?user_id=1")
    print("Get Alerts:", response.status_code, response.json())

def test_update_alert():
    alert_id = 1  # Example alert_id
    response = requests.put(f"{BASE_URL}/alert?alert_id={alert_id}&user_id=1", json={
        "ticker": "MARI",
        "tp1": 575,
        "tp2": 585,
        "tp3": 595,
        "sl": 565,
        "box_break": 555,
        "buy_price": 565,
        "shares": 15
    })
    print("Update Alert:", response.status_code, response.text)

def test_delete_alert():
    alert_id = 1  # Example alert_id
    user_id = 1  # Example user_id
    response = requests.delete(f"{BASE_URL}/alert?alert_id={alert_id}&user_id={user_id}")
    print("Delete Alert:", response.status_code, response.json())

def test_get_tickers():
    response = requests.get(f"{BASE_URL}/tickers") 
    print("Get Tickers:", response.status_code, response.json())
    
    # Save tickers to a JSON file
    import json
    with open("data/tickers.json", "w") as f:
        json.dump(response.json(), f, indent=4)
    print(f"Tickers saved to tickers.json")

def test_get_ticker():
    response = requests.get(f"{BASE_URL}/tickers/MARI")
    print("Get Ticker:", response.status_code, response.json())

if __name__ == "__main__":
    # test_register_user()
    # test_login()
    # test_create_alert()
    test_get_alerts()
    # test_update_alert()
    # test_delete_alert()
    # test_get_alerts()
    # test_get_tickers()
    # test_check_alerts()
    # get_stock_price("MARI")
    # test_get_ticker()