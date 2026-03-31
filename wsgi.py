import os
import sys

# Adiciona o diretório raiz do projeto ao sys.path
basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from app import create_app, db
from app.models.termo import Termo
# --- INÍCIO DA MUDANÇA ---
# Importa o novo modelo para que o 'flask init_db' o encontre
from app.models.item_equipamento import ItemEquipamento
# --- FIM DA MUDANÇA ---

config_name = os.environ.get('FLASK_CONFIG') or 'default'
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    # Adiciona o novo modelo ao contexto da shell
    return dict(app=app, db=db, Termo=Termo, ItemEquipamento=ItemEquipamento)

@app.cli.command("init_db")
def init_db_command():
    with app.app_context():
        print("Inicializando o banco de dados...")
        db.create_all()
        print("Banco de dados inicializado com sucesso.")

if __name__ == '__main__':
    # (Lógica de 'init_db' direto)
    if len(sys.argv) > 1 and sys.argv[1] == 'init_db':
        with app.app_context():
            print("Inicializando o banco de dados (via execução direta)...")
            db.create_all()
            print("Banco de dados inicializado com sucesso.")
    else:
        app.run()
