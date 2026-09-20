-- =====================================================================
-- Slotly - Script de criação do banco de dados
-- Compatível com Oracle 12c ou superior (usa IDENTITY)
-- =====================================================================

-- ---------------------------------------------------------------------
-- (OPCIONAL) RESET: descomente para apagar tudo e recriar do zero.
-- Se as tabelas ainda não existem, o Oracle vai mostrar ORA-00942.
-- Isso é normal e pode ser ignorado.
-- ---------------------------------------------------------------------
-- DROP TABLE SLT_AGENDAMENTO      CASCADE CONSTRAINTS PURGE;
-- DROP TABLE SLT_BLOQUEIO         CASCADE CONSTRAINTS PURGE;
-- DROP TABLE SLT_HORARIO_TRABALHO CASCADE CONSTRAINTS PURGE;
-- DROP TABLE SLT_SERVICO          CASCADE CONSTRAINTS PURGE;
-- DROP TABLE SLT_USUARIO          CASCADE CONSTRAINTS PURGE;


-- ---------------------------------------------------------------------
-- SLT_USUARIO: clientes e o barbeiro (diferenciados por perfil_usuario)
-- ---------------------------------------------------------------------
CREATE TABLE SLT_USUARIO (
    id_usuario      NUMBER GENERATED ALWAYS AS IDENTITY,
    nome_usuario    VARCHAR2(150)                    NOT NULL,
    email_usuario   VARCHAR2(150)                    NOT NULL,
    senha_hash      VARCHAR2(255)                    NOT NULL,
    telefone        VARCHAR2(20),
    perfil_usuario  VARCHAR2(10) DEFAULT 'CLIENTE'   NOT NULL,
    CONSTRAINT SLT_USUARIO_PK      PRIMARY KEY (id_usuario),
    CONSTRAINT uk_usuario_email   UNIQUE (email_usuario),
    CONSTRAINT ck_usuario_perfil  CHECK (perfil_usuario IN ('CLIENTE', 'BARBEIRO')),
    -- e-mail sempre em minúsculas: faz o UNIQUE valer sem diferenciar maiúsculas
    CONSTRAINT ck_usuario_email_minusculo CHECK (email_usuario = LOWER(email_usuario))
);


-- ---------------------------------------------------------------------
-- SLT_SERVICO: serviços oferecidos (duração em minutos)
-- ---------------------------------------------------------------------
CREATE TABLE SLT_SERVICO (
    id_servico   NUMBER GENERATED ALWAYS AS IDENTITY,
    nome         VARCHAR2(255)               NOT NULL,
    descricao    VARCHAR2(255),
    duracao_min  NUMBER(4)                   NOT NULL,
    preco        NUMBER(8,2)                 NOT NULL,
    ativo        CHAR(1) DEFAULT 'S'         NOT NULL,
    CONSTRAINT SLT_SERVICO_PK      PRIMARY KEY (id_servico),
    CONSTRAINT ck_servico_duracao CHECK (duracao_min > 0),
    CONSTRAINT ck_servico_preco   CHECK (preco >= 0),
    CONSTRAINT ck_servico_ativo   CHECK (ativo IN ('S', 'N'))
);


-- ---------------------------------------------------------------------
-- SLT_HORARIO_TRABALHO: regra semanal (0 = segunda ... 6 = domingo)
-- Pode haver mais de uma linha por dia (ex.: 09:00-12:00 e 14:00-18:00)
-- ---------------------------------------------------------------------
CREATE TABLE SLT_HORARIO_TRABALHO (
    id_horario   NUMBER GENERATED ALWAYS AS IDENTITY,
    dia_semana   NUMBER(1)                   NOT NULL,
    hora_inicio  VARCHAR2(5)                 NOT NULL,
    hora_fim     VARCHAR2(5)                 NOT NULL,
    ativo        CHAR(1) DEFAULT 'S'         NOT NULL,
    CONSTRAINT SLT_HORARIO_TRABALHO_PK PRIMARY KEY (id_horario),
    CONSTRAINT ck_horario_dia      CHECK (dia_semana BETWEEN 0 AND 6),
    CONSTRAINT ck_horario_ativo    CHECK (ativo IN ('S', 'N')),
    -- formato HH:MM com zero à esquerda (ex.: '09:00', nunca '9:00')
    CONSTRAINT ck_horario_formato  CHECK (
        REGEXP_LIKE(hora_inicio, '^([01][0-9]|2[0-3]):[0-5][0-9]$')
        AND REGEXP_LIKE(hora_fim, '^([01][0-9]|2[0-3]):[0-5][0-9]$')
    ),
    CONSTRAINT ck_horario_intervalo CHECK (hora_fim > hora_inicio)
);


-- ---------------------------------------------------------------------
-- SLT_BLOQUEIO: exceções pontuais (folgas, feriados, horários bloqueados)
-- ---------------------------------------------------------------------
CREATE TABLE SLT_BLOQUEIO (
    id_bloqueio  NUMBER GENERATED ALWAYS AS IDENTITY,
    data_inicio  TIMESTAMP                   NOT NULL,
    data_fim     TIMESTAMP                   NOT NULL,
    motivo       VARCHAR2(150),
    CONSTRAINT SLT_BLOQUEIO_PK       PRIMARY KEY (id_bloqueio),
    CONSTRAINT ck_bloqueio_periodo  CHECK (data_fim > data_inicio)
);


-- ---------------------------------------------------------------------
-- SLT_AGENDAMENTO: centro do sistema
-- Status que OCUPAM o horário: CONFIRMADO (e CONCLUIDO, no passado)
-- Status que LIBERAM o horário: CANCELADO
-- ---------------------------------------------------------------------
CREATE TABLE SLT_AGENDAMENTO (
    id_agendamento     NUMBER GENERATED ALWAYS AS IDENTITY,
    id_usuario         NUMBER                                NOT NULL,
    id_servico         NUMBER                                NOT NULL,
    data_hora_inicio   TIMESTAMP                             NOT NULL,
    data_hora_fim      TIMESTAMP                             NOT NULL,
    status             VARCHAR2(15) DEFAULT 'CONFIRMADO'     NOT NULL,
    data_criacao       TIMESTAMP DEFAULT SYSTIMESTAMP        NOT NULL,
    data_cancelamento  TIMESTAMP,
    CONSTRAINT SLT_AGENDAMENTO_PK        PRIMARY KEY (id_agendamento),
    CONSTRAINT ck_agendamento_periodo   CHECK (data_hora_fim > data_hora_inicio),
    CONSTRAINT ck_agendamento_status    CHECK (status IN ('CONFIRMADO', 'CANCELADO', 'CONCLUIDO')),
    CONSTRAINT SLT_AGENDAMENTO_SLT_USUARIO_FK FOREIGN KEY (id_usuario)
        REFERENCES SLT_USUARIO (id_usuario),
    CONSTRAINT SLT_AGENDAMENTO_SLT_SERVICO_FK FOREIGN KEY (id_servico)
        REFERENCES SLT_SERVICO (id_servico)
);


-- ---------------------------------------------------------------------
-- ÍNDICES: o Oracle NÃO cria índice automático para FK.
-- Estes aceleram "agendamentos do cliente X" e a checagem de conflitos.
-- ---------------------------------------------------------------------
CREATE INDEX ix_agendamento_usuario ON SLT_AGENDAMENTO (id_usuario);
CREATE INDEX ix_agendamento_servico ON SLT_AGENDAMENTO (id_servico);
CREATE INDEX ix_agendamento_inicio  ON SLT_AGENDAMENTO (data_hora_inicio);
