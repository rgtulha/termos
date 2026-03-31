import os
from dotenv import load_dotenv

# Encontra o caminho absoluto do diretório do projeto
basedir = os.path.abspath(os.path.dirname(__file__))

# Carrega variáveis de ambiente do arquivo .env (se existir)
# Isso é essencial para não "hardcodar" senhas no código.
# Você precisará criar um arquivo .env na raiz.
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    Classe de configuração base.
    Define padrões que são compartilhados entre todos os ambientes.
    """
    # Chave secreta para Flask (essencial para sessões e segurança)
    # Em produção, ISSO DEVE ser uma string complexa e lida do ambiente.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-dificil-de-adivinhar'

    # Desativa um warning do SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Define os caminhos para os templates e documentos gerados
    # Usamos 'basedir' para garantir que os caminhos funcionem em qualquer S.O.
    # Note que o __init__.py faz referência a estes caminhos.
    TEMPLATE_FOLDER = os.path.join(basedir, 'docx_templates')
    GENERATED_DOCS_FOLDER = os.path.join(basedir, 'generated_docs') # Pasta para salvar PDFs/DOCX

    # --- Configurações do Active Directory ---
    # Lidas do .env para segurança.
    # Baseado no seu ad_integration.py
    AD_SERVER = os.environ.get('AD_SERVER')
    AD_PORT = int(os.environ.get('AD_PORT', 389)) # 389 é a porta padrão LDAP
    AD_BASE_DN = os.environ.get('AD_BASE_DN')
    AD_USER_DN = os.environ.get('AD_USER_DN') # DN do usuário de "bind" (leitura)
    AD_PASSWORD = os.environ.get('AD_PASSWORD') # Senha do usuário de "bind"
    
    # Filtro de busca (como definido em ad_integration.py)
    AD_USER_SEARCH_FILTER = '(&(objectClass=user)(sAMAccountName={0}))'
    
    # Atributos que queremos buscar no AD
    # Você mencionou 'cn' (nome) e 'description' (para CPF).
    AD_USER_ATTRIBUTES = ['cn', 'description'] # Ajuste se o CPF estiver em outro campo

    @staticmethod
    def init_app(app):
        # Método estático para inicializações específicas (se necessário)
        pass

class DevelopmentConfig(Config):
    """
    Configurações para o ambiente de Desenvolvimento.
    """
    DEBUG = True
    
    # String de conexão do MySQL (lida do .env)
    # Formato: mysql+pymysql://usuario:senha@host/database
    DB_USER = os.environ.get('DB_USER') or 'termos_user'
    DB_PASS = os.environ.get('DB_PASS') or 'sua_senha_segura'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_NAME = os.environ.get('DB_NAME') or 'termos_db'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

class ProductionConfig(Config):
    """
    Configurações para o ambiente de Produção.
    """
    DEBUG = False
    
    # Em produção, a URL do banco DEVE ser lida de uma variável de ambiente.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # (Opcional, mas recomendado) Implementar logging em arquivo
    # ...

# Dicionário que mapeia o nome do ambiente (string) para a classe de config
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
