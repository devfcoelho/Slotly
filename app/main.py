import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask.cli import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

db = SQLAlchemy(app)
@app.route("/")
def inicio():
    return "Olá, Slotly"
