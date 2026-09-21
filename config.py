import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _montar_database_url():
    # Se DATABASE_URL vier pronta no ambiente, usa ela direto.
    url_pronta = os.environ.get("DATABASE_URL")
    if url_pronta:
        return url_pronta

    # Senão, monta a partir das variáveis separadas (mais fácil de configurar no .env).
    usuario = os.environ.get("DB_USER", "florescer")
    senha = quote_plus(os.environ.get("DB_PASSWORD", ""))
    host = os.environ.get("DB_HOST", "localhost")
    porta = os.environ.get("DB_PORT", "3306")
    nome_banco = os.environ.get("DB_NAME", "florescer")

    return f"mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{nome_banco}?charset=utf8mb4"


class Config:
    # Em produção, defina SECRET_KEY como variável de ambiente (não deixe fixo no código).
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")

    SQLALCHEMY_DATABASE_URI = _montar_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,  # evita erro de conexão caída do MariaDB por timeout
        "pool_pre_ping": True,
    }
