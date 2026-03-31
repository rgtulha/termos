from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
from app.utils.ad_integration import ADIntegration
from app.utils.doc_generator import DocGenerator
import os
import datetime

from app import db
from app.models.termo import Termo
from app.models.item_equipamento import ItemEquipamento

main = Blueprint('main', __name__)

@main.route('/')
def index():
    template_folder = current_app.config['TEMPLATE_FOLDER']
    try:
        templates = [f for f in os.listdir(template_folder) if f.endswith(('.docx'))]
    except FileNotFoundError:
        templates = []
    return render_template('index.html', templates=templates)

@main.route('/search_user', methods=['POST'])
def search_user():
    username = request.form.get('username')
    if not username:
        return jsonify({'error': 'Nome de usuário não fornecido'}), 400
    ad = ADIntegration()
    user_data = ad.search_users(username)
    if user_data is not None:
        return jsonify(user_data)
    else:
        return jsonify({'error': 'Falha ao consultar o Active Directory'}), 500

@main.route('/generate_term', methods=['POST'])
def generate_term():
    data = request.json
    required_fields = ['template_name', 'user_name', 'user_cpf', 'itens']
    if not all(field in data for field in required_fields) or not data['itens']:
        return jsonify({'error': 'Dados incompletos (faltam dados do termo ou itens).'}), 400

    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        nome_arquivo_unico = f"termo_{data['user_name'].replace(' ','_')}_{timestamp}.pdf"
        
        data_validade_obj = None
        if data.get('data_validade'):
            data_validade_obj = datetime.datetime.strptime(data['data_validade'], '%Y-%m-%d').date()

        novo_termo = Termo(
            tipo_termo = data['template_name'],
            nome_usuario = data['user_name'],
            cpf_usuario = data['user_cpf'],
            nome_arquivo = nome_arquivo_unico,
            gerado_por = "sistema",
            data_validade = data_validade_obj,
            unidade_origem = data.get('unidade_origem'),
            unidade_destino = data.get('unidade_destino')
        )
        db.session.add(novo_termo)
        db.session.flush()

        for item_json in data['itens']:
            novo_item = ItemEquipamento(
                descricao = item_json['descricao'],
                patrimonio = item_json['patrimonio'],
                estado = item_json['estado'],
                termo_id = novo_termo.id
            )
            db.session.add(novo_item)
        
        db.session.commit()
        return jsonify({'message': 'Termo salvo com sucesso!', 'termo': novo_termo.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Falha ao salvar no banco de dados: {e}")
        return jsonify({'error': f'Falha ao salvar no banco de dados: {str(e)}'}), 500

@main.route('/get_terms', methods=['GET'])
def get_terms():
    """
    Modificado para buscar os 5 últimos termos.
    """
    try:
        # --- ESTA FOI A ÚNICA MUDANÇA ---
        termos_recentes = Termo.query.options(
            db.joinedload(Termo.itens)
        ).order_by(Termo.data_geracao.desc()).limit(5).all()
        # --- FIM DA MUDANÇA ---
        
        termos_list = [termo.to_dict() for termo in termos_recentes]
        return jsonify(termos_list)
        
    except Exception as e:
        current_app.logger.error(f"Falha ao buscar termos: {e}")
        return jsonify({'error': f'Falha ao buscar termos: {str(e)}'}), 500


@main.route('/download_termo/<int:termo_id>', methods=['GET'])
def download_termo(termo_id):
    try:
        termo = Termo.query.options(db.joinedload(Termo.itens)).get(termo_id)
        if not termo:
            return jsonify({'error': 'Termo não encontrado'}), 404

        validade_formatada = ''
        if termo.data_validade:
            validade_formatada = termo.data_validade.strftime("%d/%m/%Y")

        context = {
            'NOME_COMPLETO': termo.nome_usuario,
            'CPF': termo.cpf_usuario, 
            'CARGO': 'Assessor', 
            'DATA_ATUAL': termo.data_geracao.strftime("%d/%m/%Y"), 
            'VALIDADE_ATE': validade_formatada,
            'UNIDADE_ORIGEM': termo.unidade_origem or '',
            'UNIDADE_DESTINO': termo.unidade_destino or '',
        }
        
        generator = DocGenerator(termo.tipo_termo)
        pdf_filename = generator.generate_document(context, termo.itens)

        return send_from_directory(
            current_app.config['GENERATED_DOCS_FOLDER'],
            pdf_filename,
            as_attachment=True
        )
    except FileNotFoundError as e:
        current_app.logger.error(f"Template DOCX não encontrado: {e}")
        return jsonify({'error': f'Template {termo.tipo_termo} não encontrado no servidor.'}), 404
    except Exception as e:
        current_app.logger.error(f"Falha ao gerar PDF (ID: {termo_id}): {e}")
        return jsonify({'error': f'Falha interna ao gerar o PDF: {str(e)}'}), 500
