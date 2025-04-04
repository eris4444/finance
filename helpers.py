import requests
import urllib.parse
from flask import redirect, render_template, session
from functools import wraps

def apology(message, code=400):
    return render_template("apology.html", message=message), code

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def lookup(symbol):
    try:
        response = requests.get(f"https://api.iex.cloud/v1/data/core/quote/{symbol}?token=YOUR_API_KEY")
        data = response.json()
        return {"name": data["companyName"], "price": float(data["latestPrice"]), "symbol": data["symbol"]}
    except:
        return None

def usd(value):
    return f"${value:,.2f}"
