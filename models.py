from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db

# Papéis possíveis para usuários da equipe (tipo="equipe")
PAPEIS_EQUIPE = ["admin", "terapeuta", "secretaria"]

# Situações possíveis de um agendamento
STATUS_AGENDAMENTO = ["agendado", "realizado", "cancelado", "falta"]

# Tabela de associação: um paciente pode ter mais de um responsável,
# e um responsável pode ter mais de um paciente (ex: irmãos).
paciente_responsavel = db.Table(
    "paciente_responsavel",
    db.Column("paciente_id", db.Integer, db.ForeignKey("paciente.id"), primary_key=True),
    db.Column("usuario_id", db.Integer, db.ForeignKey("usuario.id"), primary_key=True),
)


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)

    # "equipe" ou "responsavel"
    tipo = db.Column(db.String(20), nullable=False)

    # Só usado quando tipo == "equipe": admin | terapeuta | secretaria
    papel = db.Column(db.String(20), nullable=True)

    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Pacientes atribuídos a este usuário quando ele é terapeuta
    pacientes_como_terapeuta = db.relationship(
        "Paciente", back_populates="terapeuta", foreign_keys="Paciente.terapeuta_id"
    )

    # Pacientes vinculados a este usuário quando ele é responsável
    pacientes_como_responsavel = db.relationship(
        "Paciente", secondary=paciente_responsavel, back_populates="responsaveis"
    )

    def set_senha(self, senha_texto_puro):
        self.senha_hash = generate_password_hash(senha_texto_puro)

    def checar_senha(self, senha_texto_puro):
        return check_password_hash(self.senha_hash, senha_texto_puro)

    @property
    def is_equipe(self):
        return self.tipo == "equipe"

    @property
    def is_responsavel(self):
        return self.tipo == "responsavel"

    @property
    def is_admin(self):
        return self.tipo == "equipe" and self.papel == "admin"

    def __repr__(self):
        return f"<Usuario {self.email} ({self.tipo}/{self.papel})>"


class Paciente(db.Model):
    __tablename__ = "paciente"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(160), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    terapeuta_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)
    terapeuta = db.relationship(
        "Usuario", back_populates="pacientes_como_terapeuta", foreign_keys=[terapeuta_id]
    )

    responsaveis = db.relationship(
        "Usuario", secondary=paciente_responsavel, back_populates="pacientes_como_responsavel"
    )

    def __repr__(self):
        return f"<Paciente {self.nome}>"


class Agendamento(db.Model):
    __tablename__ = "agendamento"

    id = db.Column(db.Integer, primary_key=True)

    paciente_id = db.Column(db.Integer, db.ForeignKey("paciente.id"), nullable=False)
    paciente = db.relationship("Paciente", backref=db.backref("agendamentos", lazy="dynamic"))

    terapeuta_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    terapeuta = db.relationship("Usuario", backref=db.backref("agendamentos", lazy="dynamic"))

    data_hora = db.Column(db.DateTime, nullable=False)
    duracao_minutos = db.Column(db.Integer, nullable=False, default=50)

    status = db.Column(db.String(20), nullable=False, default="agendado")
    observacao = db.Column(db.String(500), nullable=True)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Agendamento {self.paciente_id} em {self.data_hora}>"


class Evolucao(db.Model):
    """Registro clínico de uma sessão — visível só pra equipe (admin/terapeuta),
    nunca pra secretaria nem pro responsável."""

    __tablename__ = "evolucao"

    id = db.Column(db.Integer, primary_key=True)

    paciente_id = db.Column(db.Integer, db.ForeignKey("paciente.id"), nullable=False)
    paciente = db.relationship("Paciente", backref=db.backref("evolucoes", lazy="dynamic"))

    terapeuta_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    terapeuta = db.relationship("Usuario", backref=db.backref("evolucoes", lazy="dynamic"))

    agendamento_id = db.Column(db.Integer, db.ForeignKey("agendamento.id"), nullable=True)
    agendamento = db.relationship("Agendamento", backref=db.backref("evolucao", uselist=False))

    data = db.Column(db.Date, nullable=False)
    texto = db.Column(db.Text, nullable=False)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Evolucao paciente={self.paciente_id} em {self.data}>"


class TarefaCasa(db.Model):
    """Tarefa proposta pelo terapeuta pra ser feita em casa. Visível pro
    responsável marcar como concluída."""

    __tablename__ = "tarefa_casa"

    id = db.Column(db.Integer, primary_key=True)

    paciente_id = db.Column(db.Integer, db.ForeignKey("paciente.id"), nullable=False)
    paciente = db.relationship("Paciente", backref=db.backref("tarefas", lazy="dynamic"))

    criado_por_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    criado_por = db.relationship("Usuario")

    titulo = db.Column(db.String(160), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    prazo = db.Column(db.Date, nullable=True)

    concluida = db.Column(db.Boolean, default=False, nullable=False)
    concluida_em = db.Column(db.DateTime, nullable=True)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TarefaCasa {self.titulo} paciente={self.paciente_id}>"


class Mensagem(db.Model):
    """Comunicação entre equipe e responsável, sempre atrelada a um paciente."""

    __tablename__ = "mensagem"

    id = db.Column(db.Integer, primary_key=True)

    paciente_id = db.Column(db.Integer, db.ForeignKey("paciente.id"), nullable=False)
    paciente = db.relationship("Paciente", backref=db.backref("mensagens", lazy="dynamic"))

    autor_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    autor = db.relationship("Usuario")

    texto = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Mensagem paciente={self.paciente_id} de {self.autor_id}>"
