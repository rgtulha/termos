
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Lista temporária para armazenar os termos gerados (substituiremos por um banco de dados)
termos_gerados = []

@app.route('/')
def index():
    """Página inicial que lista os termos gerados."""
    return render_template('index.html', termos=termos_gerados)

@app.route('/criar', methods=['GET', 'POST'])
def criar_termo():
    """Página para criar um novo termo."""
    if request.method == 'POST':
        # Lógica para processar o formulário virá aqui
        # Por enquanto, apenas redirecionamos para a página inicial
        return redirect(url_for('index'))
    
    # Dados de exemplo para o formulário
    tipos_termo = [
        'TERMO DE RESPONSABILIDADE USO TEMPORÁRIO – ENTREGA',
        'TERMO DE RESPONSABILIDADE USO TEMPORÁRIO – DEVOLUÇÃO',
        'TERMO DE RESPONSABILIDADE - TRANSFERÊNCIA INTERNA DE BENS'
    ]
    estados_equipamento = ['ÓTIMO', 'BOM', 'REGULAR', 'PÉSSIMO', 'RECUPERÁVEL', 'INUTILIZÁVEL']
    
    return render_template('criar_termo.html', tipos_termo=tipos_termo, estados_equipamento=estados_equipamento)

if __name__ == '__main__':
    app.run(debug=True)