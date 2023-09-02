from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, cryptoPriceLookup, currencyPriceLookup, digits


""" -------------- Configuration -------------- """


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["digits"] = digits

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# API key error check?


""" ------------------------------------------------ Login ------------------------------------------------ """


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Add EUR in id_currencies
        all_cur = []
        all_cur_id = db.execute("SELECT currency FROM id_currencies WHERE person_id = ?",session["user_id"])
        for cur in all_cur_id:
            cur_currency = cur["currency"]
            all_cur.append(cur_currency)

        if 'EUR' not in all_cur:
            db.execute("INSERT INTO id_currencies (person_id, currency, amount) VALUES(?, ?, ?);", session["user_id"], "EUR", 100_000)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

""" ------------------------------------------------ Password Change ------------------------------------------------ """

@app.route("/passwdchange", methods=["GET", "POST"])
def passwdchange():
    """Change User Password"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        ppassword = request.form.get("ppassword")
        npassword = request.form.get("npassword")
        p_confirmation = request.form.get("confirmation")

        usernames_dict = db.execute("SELECT username FROM users;")
        usernames = []
        for i in usernames_dict:
            for val in i.values():
                usernames.append(val)

        if not username or username not in usernames:
            return apology("Username empty or username mistyped", 400)
            
        if not ppassword or (not npassword) or (not p_confirmation):
            return apology("Some password field is empty", 400)

        if npassword != p_confirmation:
            return apology("New password does not match the confirmation", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], ppassword):
            return apology("Invalid username and/or password", 403)

        # If all test cases pass then
        hash = generate_password_hash(npassword, method='pbkdf2:sha256', salt_length=8)

        # Change the user's password into the new one
        db.execute("UPDATE users SET hash = ? WHERE username = ?", hash, username)
        return redirect("/")


    else:
        return render_template("passwdchange.html")


""" ------------------------------------------------ Logout ------------------------------------------------ """


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


""" ------------------------------------------------ Register ------------------------------------------------ """


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        p_confirmation = request.form.get("confirmation")

        usernames_dict = db.execute("SELECT username FROM users;")
        usernames = []
        for i in usernames_dict:
            for val in i.values():
                usernames.append(val)

        if not username or username in usernames:
            return apology("Username empty or username not available", 400)
        elif not password or password != p_confirmation:
            return apology("Password empty or password does not match the confirmation", 400)
        else:
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

            #Add the user's entry into the database
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?);", username, hash)            
            return redirect("/")

    else:
        return render_template("register.html")


""" ------------------------------------------------ Index ------------------------------------------------ """
@app.route("/")
@login_required
def index():
    """Show data in tables"""
    currency_data = db.execute("SELECT * FROM id_currencies WHERE person_id = ? ", session["user_id"])
    crypto_data = db.execute("SELECT * FROM id_cryptos WHERE person_id = ? ", session["user_id"])

    dataCur = {}
    dataCry = {}

    for cur in currency_data:
        currency = cur["currency"]
        amount = float(cur["amount"])
        dataCur.update({currency : amount})
    
    for cur in crypto_data:
        symbol = cur["symbol"]
        amount = float(cur["amount"])
        dataCry.update({symbol : amount})


    # --------- Currency data for right now ---------
    newdata = []
    for cur in currency_data:
        newdata.append(cur["currency"])
        
    data_dict = []

    for cur in newdata:
        if cur == "EUR":
            data_dict.append(currencyPriceLookup(cur,"USD"))
        else:
            data_dict.append(currencyPriceLookup(cur,"EUR"))


    # --------- Crypto data for right now ---------
    newdata2 = []
    for cur in crypto_data:
        newdata2.append(cur["symbol"])
        
    data_dict2 = []

    for cur in newdata2:
        data_dict2.append(cryptoPriceLookup("EUR", cur))


    try:
        return render_template("index.html", dataCry=dataCry, dataCur=dataCur, data_dict=data_dict, data_dict2=data_dict2)
    except:
        return apology("Too many API calls:( , wait one minute for more.", 403)
        


""" ------------------------------------------------ Index Add Cash ------------------------------------------------ """


@app.route("/addcash", methods=["POST"])
@login_required
def addcash():
    """Add cash to account"""
    if request.method == "POST":
        amount = int(request.form.get("amount"))
        currency = request.form.get("currency").upper()

        if not amount or (int(amount) > 100_000_000):
            return apology("Please enter a valid amount number", 403)
        
        if currencyPriceLookup(currency, "EUR") == None:
            return apology("Please enter a valid currency or wait for more API calls", 403)

        all_cur = []
        all_cur_id = db.execute("SELECT currency FROM id_currencies WHERE person_id = ?",session["user_id"])
        for cur in all_cur_id:
            cur_currency = cur["currency"]
            all_cur.append(cur_currency)

        if currency in all_cur:
            # Get the cur_cash
            cur_cash = db.execute("SELECT amount FROM id_currencies WHERE person_id = ? AND currency = ?", session["user_id"], currency)
            cur_cash = cur_cash[0]["amount"]

            db.execute("UPDATE id_currencies SET amount = ? WHERE person_id= ? AND currency = ?", (cur_cash + amount), session["user_id"], currency)
        else:
            db.execute("INSERT INTO id_currencies (person_id, currency, amount) VALUES(?, ?, ?);", session["user_id"], currency, amount)

        current_time = datetime.datetime.now()

        db.execute("INSERT INTO currencytransactions (person_id, from_cur, rate, quantity, to_cur, year, month, day, hour, minute, second) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                   session["user_id"], "From Me", 1, amount, currency, current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)

        try:
            return redirect("/")
        except:
            return apology("Too many API calls:( , wait one minute for more.", 403)


""" ------------------------------------------------ Crypto ------------------------------------------------ """

@app.route("/crypto", methods=["GET", "POST"])
@login_required
def crypto():
    """Crypto Page"""
    if request.method == "GET":
        return render_template("crypto.html")
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        currency = request.form.get("currency").upper()

        data = cryptoPriceLookup(currency, symbol)

        if not symbol or data == None:
            return apology("Symbol does not exist or wait for more API calls.", 400)
            
        try:
            return render_template("cryptoed.html", data=data)
        except:
            return apology("Too many API calls:( , wait one minute for more.", 403)
            


""" ------------------------------------------------ Exchange Crypto ------------------------------------------------ """


@app.route("/exchange", methods=["GET", "POST"])
@login_required
def exchange():
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        currency = request.form.get("currency").upper()

        data = cryptoPriceLookup(currency, symbol)

        if not symbol or data == None:
            return apology("Symbol does not exist or wait for more API calls.", 400)

        try:
            shares = float(shares)
        except:
            return apology("Input valid number of shares", 400)

        if not shares or (shares % 1 != 0) or shares == 0:
            return apology("Input valid number of shares", 400)
        
        all_cur = []
        all_cur_id = db.execute("SELECT currency FROM id_currencies WHERE person_id = ?",session["user_id"])
        for cur in all_cur_id:
            cur_currency = cur["currency"]
            all_cur.append(cur_currency)


        shares = int(shares)
        rate = float(data["exchange_rate"])

        # <------ CRYPTO BYING ------>
        if shares > 0:

            amount = rate * shares

            if currency not in all_cur:
                return apology("Input a valid currency", 400)

            # Get the cur_cash
            cur_cash = db.execute("SELECT amount FROM id_currencies WHERE person_id = ? AND currency = ?", session["user_id"], currency)
            cur_cash = cur_cash[0]["amount"]

            # Check
            if amount > cur_cash:
                return apology("Not enough money", 403)

            current_time = datetime.datetime.now()

            db.execute("UPDATE id_currencies SET amount = ? WHERE person_id= ? AND currency = ?", (cur_cash - amount), session["user_id"], currency)
            db.execute("INSERT INTO cryptotransactions (person_id, symbol, price, quantity, currency, year, month, day, hour, minute, second) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                    session["user_id"], symbol, amount, shares, currency, current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)

        
            all_crypto = []
            all_crypto_id = db.execute("SELECT symbol FROM id_cryptos WHERE person_id = ?",session["user_id"])
            for cur in all_crypto_id:
                cur_crypto = cur["symbol"]
                all_crypto.append(cur_crypto)
        
            # If crypto
            if symbol not in all_crypto:
                db.execute("INSERT INTO id_cryptos (person_id, symbol, amount) VALUES(?, ?, ?);", session["user_id"], symbol, shares)

            else:
                cur_amount = db.execute("SELECT amount FROM id_cryptos WHERE person_id = ? AND symbol = ?", session["user_id"], symbol)
                cur_amount = cur_amount[0]["amount"]

                db.execute("UPDATE id_cryptos SET amount = ? WHERE person_id= ? AND symbol = ?", (cur_amount + shares), session["user_id"], symbol)
        

        # <------ CRYPTO SELLING ------>
        else:

            amount = ((rate * shares) *(-1))

            if currency in all_cur:

                all_crypto = []
                all_crypto_id = db.execute("SELECT symbol FROM id_cryptos WHERE person_id = ?",session["user_id"])
                for cur in all_crypto_id:
                    cur_crypto = cur["symbol"]
                    all_crypto.append(cur_crypto)
            
                # If crypto
                if symbol not in all_crypto:
                    return apology("Symbol not owned", 400)

                cur_crypto = db.execute("SELECT amount FROM id_cryptos WHERE person_id = ? AND symbol = ?", session["user_id"], symbol)
                cur_crypto = cur_crypto[0]["amount"]

                if ((-1) * shares) > cur_crypto:
                    return apology("Not enough shares", 403)

                # Get the cur_cash
                cur_cash = db.execute("SELECT amount FROM id_currencies WHERE person_id = ? AND currency = ?", session["user_id"], currency)
                cur_cash = cur_cash[0]["amount"]

                db.execute("UPDATE id_currencies SET amount = ? WHERE person_id= ? AND currency = ?", cur_cash + amount, session["user_id"], currency)
            else:
                db.execute("INSERT INTO id_currencies (person_id, currency, amount) VALUES(?, ?, ?);", session["user_id"], currency, amount)
            
            current_time = datetime.datetime.now()

            db.execute("UPDATE id_cryptos SET amount = ? WHERE person_id= ? AND symbol = ?", (cur_crypto + shares), session["user_id"], symbol)
            db.execute("INSERT INTO cryptotransactions (person_id, symbol, price, quantity, currency, year, month, day, hour, minute, second) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                        session["user_id"], symbol, amount, shares, currency, current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)

        try:
            return redirect("/")
        except:
            return apology("Too many API calls:( , wait one minute for more.", 403)
            

    else:
        return render_template("exchange.html")


""" ------------------------------------------------ Currency ------------------------------------------------ """

@app.route("/currency", methods=["GET", "POST"])
@login_required
def currency():
    """Crypto Page"""
    if request.method == "GET":
        return render_template("currency.html")
    if request.method == "POST":
        from_symbol = request.form.get("from_symbol").upper()
        to_symbol = request.form.get("to_symbol").upper()

        data = currencyPriceLookup(from_symbol, to_symbol)

        if not from_symbol or (not to_symbol) or data == None:
            return apology("Symbol does not exist or wait for more API calls.", 400)

        try:
            return render_template("currented.html", data=data)
        except:
            return apology("Too many API calls:( , wait one minute for more.", 403)
            

""" ------------------------------------------------ Exchange Currency ------------------------------------------------ """

@app.route("/exchangec", methods=["GET", "POST"])
@login_required
def exchangec():
    if request.method == "POST":
        value = request.form.get("value")
        from_currency = request.form.get("from_currency").upper()
        to_currency = request.form.get("to_currency").upper()

        data = currencyPriceLookup(from_currency, to_currency)

        if not from_currency or (not to_currency) or data == None:
            return apology("Symbol does not exist or wait for more API calls.", 400)

        try:
            value = float(value)
        except:
            return apology("Input valid number of value(int)", 400)

        if not value or value <= 0 or (value % 1 != 0):
            return apology("Input valid number of value(int)", 400)

        all_cur = []
        all_cur_id = db.execute("SELECT currency FROM id_currencies WHERE person_id = ?",session["user_id"])
        for cur in all_cur_id:
            cur_currency = cur["currency"]
            all_cur.append(cur_currency)

        value = int(value)

        rate = float(data["exchange_rate"])
        amount = rate * value

        if from_currency not in all_cur:
            return apology("You don't own that currency", 400)

        # From cur amount
        from_cur_amount = db.execute("SELECT amount FROM id_currencies WHERE person_id = ? AND currency = ?", session["user_id"], from_currency)
        from_cur_amount = from_cur_amount[0]["amount"]

        # Check
        if value > from_cur_amount:
            return apology("Not enough money", 403)

        if to_currency in all_cur:
            to_cur_amount = db.execute("SELECT amount FROM id_currencies WHERE person_id = ? AND currency = ?", session["user_id"], to_currency)
            to_cur_amount = to_cur_amount[0]["amount"]

            db.execute("UPDATE id_currencies SET amount = ? WHERE person_id= ? AND currency = ?", (to_cur_amount + amount), session["user_id"], to_currency)
        else:
            db.execute("INSERT INTO id_currencies (person_id, currency, amount) VALUES(?, ?, ?);", session["user_id"], to_currency, amount)

        db.execute("UPDATE id_currencies SET amount = ? WHERE person_id= ? AND currency = ?", (from_cur_amount - value), session["user_id"], from_currency)


        current_time = datetime.datetime.now()
        
        db.execute("INSERT INTO currencytransactions (person_id, from_cur, rate, quantity, to_cur, year, month, day, hour, minute, second) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                   session["user_id"], from_currency, rate, value, to_currency, current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
        
        try:
            return redirect("/")
        except:
            return apology("Too many API calls:( , wait one minute for more.", 403)
            
    else:
        return render_template("exchangec.html")


""" ------------------------------------------------ History ------------------------------------------------ """
@app.route("/history")
@login_required
def history():
    """Show the history of all the transactions"""

    currency_data = db.execute("SELECT * FROM currencytransactions WHERE person_id = ? ", session["user_id"])
    crypto_data = db.execute("SELECT * FROM cryptotransactions WHERE person_id = ? ", session["user_id"])

    for cur in currency_data:
        if cur["from_cur"] == 'From Me':
            continue
        else:
            from_cur = cur["from_cur"]
            to_cur = cur["to_cur"]
            new_data = currencyPriceLookup(from_cur, to_cur)
            try:
                ratenow = float(new_data["exchange_rate"])
            except:
                return apology("Too many API calls:( , wait one minute for more.", 403)
            cur.update({"ratenow" : ratenow})


    for cur in crypto_data:
        symbol = cur["symbol"]
        currency = cur["currency"]
        new_data = cryptoPriceLookup(currency, symbol)
        ratenow = float(new_data["exchange_rate"])
        cur.update({"ratenow" : ratenow})


    try:
        return render_template("history.html", currency_data=currency_data, crypto_data=crypto_data)
    except:
        return apology("Too many API calls:( , wait one minute for more.", 403)
        

""" ------------------------------------------------ END OF MAIN ------------------------------------------------ """




# --------------------------------------- FEATURES FOR NON HEAVY API USAGE --------------------------------------- #



""" ------------------------------------------------ HistoryNonRate ------------------------------------------------ """
@app.route("/historynonrate")
@login_required
def historynonrate():
    """Show the history of all the transactions"""

    currency_data = db.execute("SELECT * FROM currencytransactions WHERE person_id = ? ", session["user_id"])
    crypto_data = db.execute("SELECT * FROM cryptotransactions WHERE person_id = ? ", session["user_id"])

    return render_template("historynonrate.html", currency_data=currency_data, crypto_data=crypto_data)


""" ------------------------------------------------ IndexNonRate ------------------------------------------------ """
@app.route("/indexnonrate")
@login_required
def indexnonrate():
    """Show some data in tables"""
    currency_data = db.execute("SELECT * FROM id_currencies WHERE person_id = ? ", session["user_id"])
    crypto_data = db.execute("SELECT * FROM id_cryptos WHERE person_id = ? ", session["user_id"])

    return render_template("indexnonrate.html", currency_data=currency_data, crypto_data=crypto_data)
