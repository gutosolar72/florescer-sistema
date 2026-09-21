from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db

# Papéis possíveis para usuários da equipe (tipo="equipe")
PAPEIS_EQUIPE = ["admin", "terapeuta", "secretaria"]

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
