from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
from app.utils.ad_integration import ADIntegration
from app.utils.doc_generator import DocGenerator
import os
import datetime

from app import db
from app.models.termo import Termo

main = Blueprint('main', __name__)

# (A rota '/' não muda)
@main.route('/')
def index():
    template_folder = current_app.config['TEMPLATE_FOLDER']
    try:
        templates = [f for f in os.listdir(template_folder) if f.endswith(('.docx'))]
    except FileNotFoundError:
        templates = []
    return render_template('index.html', templates=templates)

# (A rota '/search_user' não muda)
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

# (A rota '/generate_term' é MODIFICADA)
@main.route('/generate_term', methods=['POST'])
def generate_term():
    data = request.json
    required_fields = ['template_name', 'user_name', 'user_cpf', 'equipment_description']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Dados incompletos fornecidos'}), 400

    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        nome_arquivo_unico = f"termo_{data['user_name'].replace(' ','_')}_{timestamp}.pdf"
        
        data_validade_str = data.get('data_validade')
        data_validade_obj = None
        if data_validade_str:
            data_validade_obj = datetime.datetime.strptime(data_validade_str, '%Y-%m-%d').date()

        novo_termo = Termo(
            tipo_termo = data['template_name'],
            nome_usuario = data['user_name'],
            cpf_usuario = data['user_cpf'],
            descricao_equipamento = data['equipment_description'],
            nome_arquivo = nome_arquivo_unico,
            gerado_por = "sistema",
            patrimonio = data.get('patrimonio'),
            estado_equipamento = data.get('estado_equipamento'),
            data_validade = data_validade_obj,
            
            # --- INÍCIO DA MUDANÇA ---
            unidade_origem = data.get('unidade_origem'),
            unidade_destino = data.get('unidade_destino')
            # --- FIM DA MUDANÇA ---
        )
        db.session.add(novo_termo)
        db.session.commit()
        return jsonify({'message': 'Termo salvo com sucesso!', 'termo': novo_termo.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Falha ao salvar no banco de dados: {e}")
        return jsonify({'error': f'Falha ao salvar no banco de dados: {str(e)}'}), 500

# (A rota '/get_terms' não muda)
@main.route('/get_terms', methods=['GET'])
def get_terms():
    try:
        termos_recentes = Termo.query.order_by(Termo.data_geracao.desc()).limit(10).all()
        termos_list = [termo.to_dict() for termo in termos_recentes]
        return jsonify(termos_list)
    except Exception as e:
        current_app.logger.error(f"Falha ao buscar termos: {e}")
        return jsonify({'error': f'Falha ao buscar termos: {str(e)}'}), 500


# (A rota '/download_termo' é MODIFICADA)
@main.route('/download_termo/<int:termo_id>', methods=['GET'])
def download_termo(termo_id):
    """
    Gera e envia o PDF "sob demanda" com o mapeamento CORRETO dos campos.
    """
    try:
        termo = Termo.query.get_or_404(termo_id)

        validade_formatada = ''
        if termo.data_validade:
            validade_formatada = termo.data_validade.strftime("%d/%m/%Y")

        context = {
            # Campos do Usuário
            'NOME_COMPLETO': termo.nome_usuario,
            'CPF': termo.cpf_usuario, 
            'CARGO': 'Assessor', 

            # Campos do Equipamento
            'NOME_EQUIPAMENTO': termo.descricao_equipamento,
            'PATRIMONIO': termo.patrimonio or '',
            'ESTADO': termo.estado_equipamento or '',
            
            # Campos de Data e Controle
            'DATA_ATUAL': termo.data_geracao.strftime("%d/%m/%Y"), 
            'VALIDADE_ATE': validade_formatada,
            'SEQUENCIA': '1',
            
            # --- INÍCIO DA MUDANÇA ---
            # Mapeia para os *novos* placeholders que você vai criar no .docx
            'UNIDADE_ORIGEM': termo.unidade_origem or '',
            'UNIDADE_DESTINO': termo.unidade_destino or '',
            # Removemos o placeholder ambíguo
            # 'NOME_DEPARTAMENTO': 'GERÊNCIA DE TI' 
            # --- FIM DA MUDANÇA ---
        }

        generator = DocGenerator(termo.tipo_termo)
        pdf_filename = generator.generate_document(context)

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
