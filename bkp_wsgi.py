import os
import sys

# Adiciona o diretório raiz do projeto ao sys.path
basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from app import create_app, db
from app.models.termo import Termo

config_name = os.environ.get('FLASK_CONFIG') or 'default'
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Termo=Termo)

@app.cli.command("init_db")
def init_db_command():
    with app.app_context():
        print("Inicializando o banco de dados...")
        db.create_all()
        print("Banco de dados inicializado com sucesso.")

if __name__ == '__main__':
    app.run()
