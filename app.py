from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# =======================
# OSNOVNA NASTAVITEV
# =======================

app = Flask(__name__)
app.secret_key = "skrivni_kljuc_za_sejo"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USERS_FILE = os.path.join(BASE_DIR, "uporabniki.json")
REZERVACIJE_FILE = os.path.join(BASE_DIR, "rezervacije.json")
SPOROCILA_FILE = os.path.join(BASE_DIR, "sporocila.json")


# =======================
# POMOŽNE FUNKCIJE
# =======================

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def get_user(username):
    for u in load_users():
        if u["username"] == username:
            return u
    return None

def load_rezervacije():
    if not os.path.exists(REZERVACIJE_FILE):
        return []
    with open(REZERVACIJE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_rezervacije(rezervacije):
    with open(REZERVACIJE_FILE, "w", encoding="utf-8") as f:
        json.dump(rezervacije, f, indent=2, ensure_ascii=False)

def load_sporocila():
    if not os.path.exists(SPOROCILA_FILE):
        return []
    with open(SPOROCILA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sporocila(sporocila):
    with open(SPOROCILA_FILE, "w", encoding="utf-8") as f:
        json.dump(sporocila, f, indent=2, ensure_ascii=False)


# =======================
# JAVNE STRANI
# =======================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/storitve")
def storitve():
    return render_template("storitve.html")

@app.route("/cenik")
def cenik():
    return render_template("cenik.html")

@app.route("/rezervacija", methods=["GET", "POST"])
def rezervacija():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        nova = {
            "user": session["user"],
            "ime": request.form["ime"],
            "email": request.form["email"],
            "storitev": request.form["storitev"],
            "termin": request.form["termin"],
            "sporocilo": request.form.get("sporocilo", ""),
            "ustvarjeno": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        rezervacije = load_rezervacije()
        rezervacije.append(nova)
        save_rezervacije(rezervacije)

        return redirect(url_for("dashboard"))

    return render_template("rezervacija.html")

@app.route("/onas")
def onas():
    return render_template("onas.html")

@app.route("/galerija")
def galerija():
    return render_template("galerija.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/kontakt", methods=["GET", "POST"])
def kontakt():
    if request.method == "POST":
        sporocilo = {
            "ime": request.form["ime"],
            "email": request.form["email"],
            "sporocilo": request.form["sporocilo"],
            "ustvarjeno": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        vsa = load_sporocila()
        vsa.append(sporocilo)
        save_sporocila(vsa)

        flash("Sporočilo je bilo uspešno poslano. Hvala!")
        return redirect(url_for("kontakt"))

    return render_template("kontakt.html")


# =======================
# AVTENTIKACIJA
# =======================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["uporabnisko_ime"]
        password = request.form["geslo"]

        if get_user(username):
            flash("Uporabnik že obstaja.")
            return redirect(url_for("register"))

        users = load_users()
        users.append({
            "username": username,
            "password": generate_password_hash(password)
        })
        save_users(users)

        flash("Registracija uspešna. Prijavi se.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["uporabnisko_ime"]
        password = request.form["geslo"]

        user = get_user(username)
        if user and check_password_hash(user["password"], password):
            session["user"] = username
            return redirect(url_for("dashboard"))

        flash("Napačno uporabniško ime ali geslo.")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

# =======================
# DASHBOARD (ZAŠČITEN)
# =======================

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    vse = load_rezervacije()
    uporabnikove = [r for r in vse if r["user"] == session["user"]]

    return render_template("dashboard.html", rezervacije=uporabnikove)

# =======================
# ZAGON
# =======================

if __name__ == "__main__":
    app.run(debug=True)
