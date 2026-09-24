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

class Servico(db.Model):
    __tablename__ = "servico"

    id = db.Column(db.Integer, primary_key =True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    duracao_min = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Numeric(8,2), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (
        db.CheckConstraint("duracao_min > 0", name="ck_servico_duracao"),
        db.CheckConstraint("preco >= 0", name="ck_servico_preco"),
    )