import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config  # <-- Funciona por causa do wsgi.py

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    with app.app_context():
        if not os.path.exists(app.config['TEMPLATE_FOLDER']):
            os.makedirs(app.config['TEMPLATE_FOLDER'])
        if not os.path.exists(app.config['GENERATED_DOCS_FOLDER']):
            os.makedirs(app.config['GENERATED_DOCS_FOLDER'])

    # Importação absoluta (funciona porque app/routes/__init__.py existe)
    from app.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
