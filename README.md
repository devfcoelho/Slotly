# Slotly

Sistema de agendamento online para barbearia, feito para praticar desenvolvimento web com Python, banco de dados relacional e front end.

> 🚧 **Status:** em desenvolvimento. A modelagem do banco e a estrutura inicial da aplicação estão prontas.

## Sobre o projeto

O Slotly permite que clientes reservem horários com o barbeiro sem conflitos de agenda, e que o barbeiro controle seus dias de trabalho, folgas e atendimentos. O sistema foi pensado para um barbeiro só, com serviços de durações diferentes (corte, barba, sobrancelha...).

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
- Marcar o atendimento como concluído

**Regras do sistema**
- Impede dois agendamentos no mesmo horário
- Só permite agendar com login
- Respeita a duração de cada serviço
- Exige prazo mínimo para cancelamento

## Tecnologias

- **Backend:** Python e Flask
- **Banco de dados:** relacional (modelagem feita no Oracle SQL Developer Data Modeler)
- **Front end:** HTML, CSS e JavaScript
- **Versionamento:** Git e GitHub

## Estrutura do projeto

```
Slotly/
├── app/
│   ├── templates/    # páginas HTML
│   ├── static/       # CSS, JavaScript e imagens
│   └── main.py       # aplicação Flask
├── docs/             # documentação (MVP e script do banco)
├── requirements.txt  # dependências do projeto
└── README.md
```

## Como rodar localmente

Pré-requisitos: Python 3 e Git instalados.

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

# 5. Iniciar o servidor
flask --app app.main run --debug
```

Depois, abra `http://127.0.0.1:5000` no navegador.

## Documentação

- [`docs/Slotly.txt`](docs/Slotly.txt): definição do MVP, user stories e regras
- [`docs/slotly_ddl.sql`](docs/slotly_ddl.sql): script de criação das tabelas

## Roadmap

- [x] Planejamento e definição do MVP
- [x] Modelagem do banco de dados
- [x] Configuração do projeto e primeira rota
- [ ] Conexão com o banco e modelos (SQLAlchemy)
- [ ] CRUD de serviços
- [ ] Cadastro, login e autenticação
- [ ] Lógica de agendamento e regra de conflito
- [ ] Front end (telas e calendário)
- [ ] Validações e testes
- [ ] Deploy

### Fora do MVP (versões futuras)

Pagamento online, avaliação do atendimento, relatório de faturamento, pacotes mensais, lista de espera, lembretes e notificações por WhatsApp.

## Autor

Desenvolvido por [devfcoelho](https://github.com/devfcoelho).