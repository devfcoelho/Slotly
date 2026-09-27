# Slotly

Sistema de agendamento online para barbearia, feito para praticar desenvolvimento web com Python, banco de dados relacional e front end.

> 🚧 **Status:** em desenvolvimento. CRUD de serviços completo. Próximo passo: cadastro e login de usuários.

## Sobre o projeto

O Slotly permite que clientes reservem horários com o barbeiro sem conflitos de agenda, e que o barbeiro controle seus dias de trabalho, folgas, serviços e atendimentos. O sistema foi pensado para **um barbeiro só**, com serviços de **durações diferentes** (corte, barba, sobrancelha...).

## Funcionalidades do MVP

**Cliente**
- Criar conta e fazer login
- Ver os horários livres e escolher o serviço
- Agendar com confirmação automática
- Cancelar dentro do prazo mínimo e criar um novo agendamento

**Barbeiro**
- Definir os dias e horários de trabalho
- Bloquear folgas e horários indisponíveis
- Ver a agenda da semana
- Cadastrar, editar e desativar serviços
- Marcar o atendimento como concluído

**Regras do sistema**
- Impede dois agendamentos no mesmo horário
- Só permite agendar com login
- Respeita a duração de cada serviço
- Exige prazo mínimo para cancelamento

## Tecnologias

- **Backend:** Python e Flask
- **ORM:** SQLAlchemy (Flask-SQLAlchemy)
- **Banco de dados:** PostgreSQL (modelagem inicial feita no Oracle SQL Developer Data Modeler, documentada em `docs/`)
- **Front end:** HTML e Jinja (templates), CSS e JavaScript
- **Versionamento:** Git e GitHub

## Estrutura do projeto

```
Slotly/
├── app/
│   ├── templates/         # páginas HTML (Jinja)
│   │   ├── servicos.html
│   │   ├── novo_servico.html
│   │   └── editar_servico.html
│   ├── static/            # CSS, JavaScript e imagens
│   └── main.py            # aplicação Flask, modelos e rotas
├── docs/                  # documentação (MVP e script do banco em Oracle)
├── requirements.txt       # dependências do projeto
├── .env.example           # modelo de variáveis de ambiente
└── README.md
```

## Modelo de dados

O banco tem 5 tabelas, modeladas primeiro em Oracle (documentação em `docs/slotly_ddl.sql`) e implementadas como modelos SQLAlchemy em PostgreSQL:

- **Servico** — serviços oferecidos (nome, duração, preço, ativo)
- **Usuario** — clientes e barbeiro (nome, email, senha com hash, perfil)
- **Agendamento** — o centro do sistema, liga usuário e serviço, com status e datas
- **HorarioTrabalho** — regra semanal de expediente do barbeiro
- **Bloqueio** — exceções pontuais (folgas, feriados)

## Como rodar localmente

Pré-requisitos: Python 3, Git e PostgreSQL instalados.

```bash
# 1. Clonar o repositório
git clone https://github.com/devfcoelho/Slotly.git
cd Slotly

# 2. Criar o ambiente virtual
python -m venv venv

# 3. Ativar o ambiente virtual
source venv/Scripts/activate   # Windows (Git Bash)
# source venv/bin/activate     # Linux ou macOS

# 4. Instalar as dependências
pip install -r requirements.txt

# 5. Criar um banco PostgreSQL chamado "slotly"

# 6. Copiar o .env.example para .env e preencher com seus dados
cp .env.example .env

# 7. Criar as tabelas no banco
python -c "from app.main import app, db; app.app_context().push(); db.create_all()"

# 8. Iniciar o servidor
flask --app app.main run --debug
```

Depois, abra `http://127.0.0.1:5000` no navegador.

## Rotas disponíveis (até o momento)

| Rota | Método | Descrição |
|---|---|---|
| `/` | GET | Página inicial |
| `/servicos` | GET | Lista todos os serviços cadastrados |
| `/servicos/novo` | GET, POST | Formulário para cadastrar um serviço |
| `/servicos/<id>/editar` | GET, POST | Formulário para editar um serviço |
| `/servicos/<id>/desativar` | POST | Ativa ou desativa um serviço |

## Documentação

- [`docs/Slotly.txt`](docs/Slotly.txt): definição do MVP, user stories e regras
- [`docs/slotly_ddl.sql`](docs/slotly_ddl.sql): modelagem original do banco em Oracle

## Roadmap

- [x] Planejamento e definição do MVP
- [x] Modelagem do banco de dados (Oracle)
- [x] Configuração do projeto e primeira rota
- [x] Conexão com PostgreSQL e criação dos 5 modelos (SQLAlchemy)
- [x] CRUD de serviços (criar, listar, editar, ativar/desativar)
- [ ] Cadastro, login e autenticação (hash de senha, sessão)
- [ ] Lógica de agendamento e regra de conflito de horário
- [ ] Configuração de horários de trabalho e bloqueios (barbeiro)
- [ ] Tela de agendamento para o cliente
- [ ] Front end com CSS e melhoria visual
- [ ] Validações e testes
- [ ] Deploy

### Fora do MVP (versões futuras)

Pagamento online, avaliação do atendimento, relatório de faturamento, pacotes mensais, lista de espera, lembretes e notificações por WhatsApp.

## Autor

Desenvolvido por [devfcoelho](https://github.com/devfcoelho).