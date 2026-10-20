from werkzeug.security import generate_password_hash
from app.main import app, db, Usuario, Servico, HorarioTrabalho

with app.app_context():
    if Usuario.query.filter_by(email="barbeiro@slotly.com").first():
        print("Dados de demonstração já existem.")
    else:
        db.session.add(Usuario(nome="Barbeiro Demo", email="barbeiro@slotly.com",
                               senha_hash=generate_password_hash("demo123"), perfil="BARBEIRO"))
        db.session.add(Usuario(nome="Cliente Demo", email="cliente@slotly.com",
                               senha_hash=generate_password_hash("demo123")))

        db.session.add(Servico(nome="Corte", duracao_min=30, preco=40))
        db.session.add(Servico(nome="Barba", duracao_min=30, preco=30))
        db.session.add(Servico(nome="Corte + Barba", duracao_min=60, preco=65))

        for dia in range(0, 5):
            db.session.add(HorarioTrabalho(dia_semana=dia, hora_inicio="09:00", hora_fim="18:00"))
        db.session.add(HorarioTrabalho(dia_semana=5, hora_inicio="09:00", hora_fim="13:00"))

        db.session.commit()
        print("Dados de demonstração criados.")