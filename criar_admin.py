"""
Script pra criar o primeiro usuário admin (roda uma vez só, na primeira
configuração do sistema, ou sempre que precisar resetar o acesso).

Uso:
    python criar_admin.py
"""
import getpass

from app import app
from extensions import db
from models import Usuario

with app.app_context():
    db.create_all()

    print("Criar usuário administrador da Florescer")
    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip().lower()
    senha = getpass.getpass("Senha: ")

    if Usuario.query.filter_by(email=email).first():
        print("Já existe um usuário com esse e-mail.")
    else:
        admin = Usuario(nome=nome, email=email, tipo="equipe", papel="admin")
        admin.set_senha(senha)
        db.session.add(admin)
        db.session.commit()
        print(f"Usuário admin '{nome}' criado com sucesso.")
