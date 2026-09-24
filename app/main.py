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

class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20))
    perfil = db.Column(db.String(10), nullable=False, default="CLIENTE")

    __table_args__ =(
        db.CheckConstraint("perfil IN ('CLIENTE', 'BARBEIRO')", name="ck_usuario_perfil"),
    )

class Agendamento(db.Model):
    __tablename__ = "agendamento"

    id_agendamento = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id"), nullable=False)
    data_hora_inicio = db.Column(db.DateTime, nullable=False)
    data_hora_fim = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="CONFIRMADO")
    data_criacao = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    data_cancelamento = db.Column(db.DateTime)

    __table_args__ = (
        db.CheckConstraint("status IN ('CONFIRMADO', 'CANCELADO', 'CONCLUIDO')", name="ck_agendamento_status"),
        db.CheckConstraint("data_hora_fim > data_hora_inicio", name="ck_agendamento_data_hora"),
    )

class HorarioTrabalho(db.Model):
    __tablename__ = "horario_trabalho"

    id_horario = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.Integer, nullable=False)
    hora_inicio = db.Column(db.String(5), nullable=False)
    hora_fim = db.Column(db.String(5), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (
        db.CheckConstraint("dia_semana IN (1, 2, 3, 4, 5, 6, 7)", name="ck_horario_trabalho_dia_semana"),
        db.CheckConstraint("hora_fim > hora_inicio", name="ck_horario_trabalho_hora"),
    )

class Bloqueio(db.Model):
    __tablename__ = "bloqueio"

    id = db.Column(db.Integer, primary_key=True)
    data_hora_inicio = db.Column(db.DateTime, nullable=False)
    data_hora_fim = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.String(150))

    __table_args__ = (
        db.CheckConstraint("data_hora_fim > data_hora_inicio", name="ck_bloqueio_data_hora"),
    )