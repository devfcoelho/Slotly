import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db = SQLAlchemy(app)
def login_obrigatorio(funcao):
    @wraps(funcao)
    def embrulho(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect("/login")
        return funcao(*args, **kwargs)
    return embrulho

def barbeiro_obrigatorio(funcao):
    @wraps(funcao)
    def embrulho(*args, **kwargs):
        if session.get("perfil") != "BARBEIRO":
            return redirect("/login")
        return funcao(*args, **kwargs)
    return embrulho
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
        db.CheckConstraint("dia_semana IN (0, 1, 2, 3, 4, 5, 6)", name="ck_horario_trabalho_dia_semana"),
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

@app.route("/")
def inicio():
    return "Olá, Slotly"

@app.route("/servicos")
def listar_servicos():
    servicos = Servico.query.all()
    return render_template("servicos.html", servicos=servicos)

@app.route("/servicos/<int:id>/editar", methods=["GET", "POST"])
@barbeiro_obrigatorio
def editar_servico(id):
    servico = Servico.query.get_or_404(id)
    if request.method == "POST":
        servico.nome = request.form["nome"]
        servico.duracao_min = request.form["duracao_min"]
        servico.preco = request.form["preco"]
        db.session.commit()
        return redirect("/servicos")
    return render_template("editar_servico.html", servico=servico)

@app.route("/servicos/<int:id>/desativar",methods=["POST"])
@barbeiro_obrigatorio
def desativar_servico(id):
    servico = Servico.query.get_or_404(id)
    servico.ativo = not servico.ativo
    db.session.commit()
    return redirect("/servicos")


@app.route("/cadastro", methods=["GET","POST"])
def cadastro():
    if request.method =="POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        senha_hash = generate_password_hash(senha)
        novo = Usuario(nome=nome,email=email,senha_hash=senha_hash)
        db.session.add(novo)
        db.session.commit()
        return redirect("/login")
    return render_template("cadastro.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method =="POST":
        email = request.form["email"]
        senha = request.form["senha"]
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha_hash,senha):
            session["usuario_id"] = usuario.id
            session["perfil"] = usuario.perfil
            return redirect("/servicos")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario_id",None)
    session.pop("perfil",None)
    return redirect("/login")

@app.route("/horarios")
@barbeiro_obrigatorio
def listar_horarios():
    horarios = HorarioTrabalho.query.all()
    return render_template("horarios.html", horarios=horarios)

@app.route("/servicos/novo", methods=["GET", "POST"])
@barbeiro_obrigatorio
def novo_servico():
    if request.method == "POST":
        nome = request.form["nome"]
        duracao_min = request.form["duracao_min"]
        preco = request.form["preco"]
        novo = Servico(nome=nome, duracao_min=duracao_min, preco=preco)
        db.session.add(novo)
        db.session.commit()
        return redirect("/servicos")
    return render_template("novo_servico.html")

@app.route("/horarios/novo",methods=["GET","POST"])
@barbeiro_obrigatorio
def novo_horario():
    if request.method == "POST":
        dia_semana = int(request.form["dia_semana"])
        hora_inicio = request.form["hora_inicio"]
        hora_fim = request.form["hora_fim"]
        novoH = HorarioTrabalho(dia_semana=dia_semana,hora_inicio=hora_inicio,hora_fim=hora_fim)
        db.session.add(novoH)
        db.session.commit()
        return redirect("/horarios")
    return render_template("novo_horario.html")

@app.route("/horarios/<int:id>/editar",methods=["GET","POST"])
@barbeiro_obrigatorio
def editar_horario(id):
    horarios = HorarioTrabalho.query.get_or_404(id)
    if request.method =="POST":
        horarios.dia_semana = int(request.form["dia_semana"])
        horarios.hora_inicio = request.form["hora_inicio"]
        horarios.hora_fim = request.form["hora_fim"]
        db.session.commit()
        return redirect("/horarios")
    return render_template("editar_horario.html",horario=horarios)

@app.route("/horarios/<int:id>/desativar", methods=["POST"])
@barbeiro_obrigatorio
def desativar_horario(id):
    horario = HorarioTrabalho.query.get_or_404(id)
    horario.ativo = not horario.ativo
    db.session.commit()
    return redirect("/horarios")

@app.route("/bloqueios")
@barbeiro_obrigatorio
def listar_bloqueios():
    bloqueios = Bloqueio.query.all()
    return render_template("bloqueios.html", bloqueios=bloqueios)

@app.route("/bloqueios/novo",methods=["GET","POST"])
@barbeiro_obrigatorio
def novo_bloqueio():
    if request.method == "POST":
        data_hora_inicio = datetime.fromisoformat(request.form["data_hora_inicio"])
        data_hora_fim = datetime.fromisoformat(request.form["data_hora_fim"])
        motivo = request.form["motivo"]

        novo = Bloqueio(data_hora_inicio=data_hora_inicio, data_hora_fim=data_hora_fim, motivo=motivo)
        db.session.add(novo)
        db.session.commit()
        return redirect("/bloqueios")
    return render_template("novo_bloqueio.html")

@app.route("/bloqueios/<int:id>/editar", methods=["GET", "POST"])
@barbeiro_obrigatorio
def editar_bloqueio(id):
    bloqueio = Bloqueio.query.get_or_404(id)
    if request.method == "POST":
        bloqueio.data_hora_inicio = datetime.fromisoformat(request.form["data_hora_inicio"])
        bloqueio.data_hora_fim = datetime.fromisoformat(request.form["data_hora_fim"])
        bloqueio.motivo = request.form["motivo"]
        db.session.commit()
        return redirect("/bloqueios")
    return render_template("editar_bloqueio.html", bloqueio=bloqueio)

@app.route("/bloqueios/<int:id>/remover", methods=["POST"])
@barbeiro_obrigatorio
def remover_bloqueio(id):
    bloqueio = Bloqueio.query.get_or_404(id)
    db.session.delete(bloqueio)
    db.session.commit()
    return redirect("/bloqueios")


        
        
    



   





    
        

        
