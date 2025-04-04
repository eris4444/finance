import os
import sqlite3
from cs50 import SQL
from flask import Flask, render_template, request, session, redirect, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

app = Flask(__name__)
app.jinja_env.filters["usd"] = usd

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    rows = db.execute("SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0", session["user_id"])
    user = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]
    return render_template("index.html", stocks=rows, cash=user["cash"])

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return apology("تمام فیلدها را پر کنید")
        if password != confirmation:
            return apology("رمز عبور مطابقت ندارد")

        hash_password = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)
            return redirect("/login")
        except:
            return apology("نام کاربری قبلاً انتخاب شده است")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            return apology("نام کاربری یا رمز اشتباه است")

        session["user_id"] = user[0]["id"]
        return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        stock = lookup(symbol)

        if stock is None or shares <= 0:
            return apology("سهام معتبر نیست")

        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        total_price = stock["price"] * shares

        if cash < total_price:
            return apology("موجودی کافی نیست")

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)", session["user_id"], symbol, shares, stock["price"])
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_price, session["user_id"])

        return redirect("/")

    return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    rows = db.execute("SELECT * FROM transactions WHERE user_id = ?", session["user_id"])
    return render_template("history.html", transactions=rows)
