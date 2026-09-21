# Florescer Sistema

Base do sistema interno da Florescer: login, papéis de acesso (admin,
terapeuta, secretaria) e portal dos responsáveis.

## Banco de dados: MariaDB

O sistema usa MariaDB (via driver PyMySQL). Antes de rodar, crie o banco e o usuário:

```sql
CREATE DATABASE florescer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'florescer'@'localhost' IDENTIFIED BY 'escolha-uma-senha-forte';
GRANT ALL PRIVILEGES ON florescer.* TO 'florescer'@'localhost';
FLUSH PRIVILEGES;
```

Depois, copie `.env.example` para `.env` e preencha `DB_USER`, `DB_PASSWORD`,
`DB_HOST`, `DB_PORT` e `DB_NAME` com os dados reais (o `.env` nunca é
commitado, já está no `.gitignore`).

## Como rodar localmente

```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt

copy .env.example .env       # Windows (ou: cp .env.example .env no Linux/Mac)
# edite o .env com os dados do seu MariaDB

python criar_admin.py        # cria o primeiro usuário admin (também cria as tabelas)
python app.py                # sobe em http://127.0.0.1:5000
```

## Estrutura

- `app.py` — cria e configura a aplicação Flask (application factory)
- `models.py` — `Usuario` (equipe ou responsável) e `Paciente`
- `auth.py` — login/logout
- `admin.py` — área da equipe (`/admin/...`), com controle por papel
- `portal.py` — área dos responsáveis (`/portal/...`)
- `permissions.py` — decorators `@equipe_required()` e `@responsavel_required`

## Papéis

- **admin** — acesso total, único que pode criar usuários
- **terapeuta** — vê só os pacientes atribuídos a ele
- **secretaria** — acesso à agenda/cadastro (a implementar)
- **responsavel** — portal separado, só vê os próprios pacientes vinculados

## Próximos passos sugeridos

1. Cadastro de pacientes (hoje só existe o modelo, falta tela de criar/editar)
2. Vincular responsável a paciente na hora do cadastro
3. Agendamentos
4. Evoluções (registro de sessão)
