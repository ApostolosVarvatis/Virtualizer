from flask import redirect, render_template, session
from functools import wraps
import requests


# Digits helper

def digits(value):
    return f"{value:,.2f}"



# Require login function

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Error message page

def apology(message, code=400):
    """Render message as an apology to user."""

    return render_template("apology.html", top=code, bottom=message), code


# <---------------------------------------------- API searches ---------------------------------------------->

# Crypto realtime exchange price

def cryptoPriceLookup(currency, crypto):

    # API Call
    try:
        url = "https://alpha-vantage.p.rapidapi.com/query"

        querystring = {"to_currency": currency,"function":"CURRENCY_EXCHANGE_RATE","from_currency": crypto}

        headers = {
            "X-RapidAPI-Key": "-",
            "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        
    except requests.RequestException:
        return None

    # Extract data
    try:
        data = response.json()
        return {
            "from_name": data["Realtime Currency Exchange Rate"]["2. From_Currency Name"],
            "to_name": data["Realtime Currency Exchange Rate"]["4. To_Currency Name"],
            "exchange_rate": float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]),
            "last_refreshed": data["Realtime Currency Exchange Rate"]["6. Last Refreshed"],
            "time_zone": data["Realtime Currency Exchange Rate"]["7. Time Zone"],
            "from_symbol": data["Realtime Currency Exchange Rate"]["1. From_Currency Code"],
            "to_symbol": data["Realtime Currency Exchange Rate"]["3. To_Currency Code"]
        }
    except (KeyError, TypeError, ValueError):
        return None


# Currency realtime exchange price

def currencyPriceLookup(from_currency, to_currency):

    # API Call
    try:
        url = "https://alpha-vantage.p.rapidapi.com/query"

        querystring = {"from_currency": from_currency,"function":"CURRENCY_EXCHANGE_RATE","to_currency": to_currency}

        headers = {
            "X-RapidAPI-Key": "-",
            "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        
    except requests.RequestException:
        return None

    # Extract data
    try:
        data = response.json()
        return {
            "from_name": data["Realtime Currency Exchange Rate"]["2. From_Currency Name"],
            "to_name": data["Realtime Currency Exchange Rate"]["4. To_Currency Name"],
            "exchange_rate": float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]),
            "last_refreshed": data["Realtime Currency Exchange Rate"]["6. Last Refreshed"],
            "time_zone": data["Realtime Currency Exchange Rate"]["7. Time Zone"],
            "from_symbol": data["Realtime Currency Exchange Rate"]["1. From_Currency Code"],
            "to_symbol": data["Realtime Currency Exchange Rate"]["3. To_Currency Code"]
        }
    except (KeyError, TypeError, ValueError):
        return None
