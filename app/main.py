import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta, time, date

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

def horarios_livres(dia):
    dia_semana_numero = dia.weekday()
    horario = HorarioTrabalho.query.filter_by(dia_semana=dia_semana_numero).first()
    if horario is None:
        return []
    inicio = datetime.strptime(horario.hora_inicio, "%H:%M").time()
    fim = datetime.strptime(horario.hora_fim, "%H:%M").time()
    atual = datetime.combine(dia,inicio)
    limite = datetime.combine(dia,fim)
    horarios= []
    while atual < limite:
        horarios.append(atual) 
        atual = atual + timedelta(minutes=30)
    
    inicio_dia = datetime.combine(dia, time(0, 0))
    dia_seguinte = inicio_dia + timedelta(days=1)
    agendamentos = Agendamento.query.filter(Agendamento.data_hora_inicio >= inicio_dia, Agendamento.data_hora_inicio < dia_seguinte).all()
    bloqueios = Bloqueio.query.filter(Bloqueio.data_hora_inicio >= inicio_dia, Bloqueio.data_hora_inicio < dia_seguinte).all()
    livres = []
    for h in horarios:
        fim_de_h = h + timedelta(minutes=30)
        ocupado = False
        for a in agendamentos:
            if h < a.data_hora_fim and fim_de_h > a.data_hora_inicio:
                ocupado = True
        for b in bloqueios:
            if h < b.data_hora_fim and fim_de_h > b.data_hora_inicio:
                ocupado = True
        if not ocupado:
            livres.append(h)
    return livres

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
    id_servico = db.Column(db.Integer,  db.ForeignKey("servico.id"), nullable=False)
    servico = db.relationship("Servico")
    usuario = db.relationship("Usuario")
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
@barbeiro_obrigatorio
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
            if usuario.perfil =="BARBEIRO":
                return redirect("/agenda")
            else:
                return redirect("/agendar")
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

@app.route("/agendar")
@login_obrigatorio
def agendar():
    servico = Servico.query.filter_by(ativo=True).all()
    return render_template("agendar.html",servicos=servico)

@app.route("/agendar/horarios")
@login_obrigatorio
def ver_horarios():
    servico_id = request.args.get('servico_id')
    data_texto = request.args.get('data')
    data_objeto = date.fromisoformat(data_texto)
    lista_horarios = horarios_livres(data_objeto)
    return render_template("agendar_horarios.html",servico_id=servico_id,lista_horarios=lista_horarios)

@app.route("/agendar/confirmar", methods=["POST"])
@login_obrigatorio
def confirmar_agendamento():
    servico_id = request.form.get("servico_id")
    horario_texto = request.form.get("horario")
    inicio = datetime.fromisoformat(horario_texto)
    
    servico = Servico.query.get_or_404(servico_id)
    horario_fim = inicio + timedelta(minutes=servico.duracao_min)
    
    usuario_id = session["usuario_id"]
    
    novo_agendamento = Agendamento(
        id_usuario=usuario_id,
        id_servico=servico_id,
        data_hora_inicio=inicio,
        data_hora_fim=horario_fim,
        status="CONFIRMADO"
    )
    db.session.add(novo_agendamento)
    db.session.commit()
    
    return redirect("/agendar")

@app.route("/meus-agendamentos")
@login_obrigatorio
def meus_agendamentos():
    usuario_id = session["usuario_id"]
    agendamentos = Agendamento.query.filter_by(id_usuario=usuario_id).all()
    return render_template("meus_agendamentos.html",usuario_id=usuario_id,agendamentos=agendamentos)

@app.route("/meus-agendamentos/<int:id>/cancelar", methods=["POST"])
@login_obrigatorio
def cancelar_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    if (agendamento.data_hora_inicio - datetime.now()) >= timedelta(hours=2):
        agendamento.status = "CANCELADO"
        agendamento.data_cancelamento = datetime.now()
        db.session.commit()
    return redirect("/meus-agendamentos")

@app.route("/agenda")
@barbeiro_obrigatorio
def agenda():
    agendamentos = Agendamento.query.filter_by(status="CONFIRMADO").order_by(Agendamento.data_hora_inicio).all()
    return render_template("agenda.html", agendamentos=agendamentos)

@app.route("/agenda/<int:id>/concluir", methods=["POST"])
@barbeiro_obrigatorio
def concluir_agendamento(id):
    agendamento = Agendamento.query.get_or_404(id)
    if  agendamento.status == "CONFIRMADO":
        agendamento.status = "CONCLUIDO"
        db.session.commit()
    return redirect("/agenda")







        
        
    



   





    
        

        
