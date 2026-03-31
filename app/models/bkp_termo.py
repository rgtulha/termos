from app import db
from datetime import datetime

class Termo(db.Model):
    """
    Modelo para armazenar os metadados dos termos gerados.
    (Atualizado com unidades de origem/destino)
    """
    __tablename__ = 'termos'

    id = db.Column(db.Integer, primary_key=True)
    tipo_termo = db.Column(db.String(100), nullable=False)
    nome_usuario = db.Column(db.String(255), nullable=False)
    cpf_usuario = db.Column(db.String(14), nullable=False)
    descricao_equipamento = db.Column(db.Text, nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False, unique=True)
    data_geracao = db.Column(db.DateTime, default=datetime.utcnow)
    gerado_por = db.Column(db.String(100)) 
    patrimonio = db.Column(db.String(100), nullable=True)
    estado_equipamento = db.Column(db.String(100), nullable=True)
    data_validade = db.Column(db.Date, nullable=True)
    
    # --- INÍCIO DA MUDANÇA ---
    unidade_origem = db.Column(db.String(100), nullable=True)
    unidade_destino = db.Column(db.String(100), nullable=True)
    # --- FIM DA MUDANÇA ---

    def __repr__(self):
        return f"<Termo {self.id} - {self.tipo_termo} para {self.nome_usuario}>"

    def to_dict(self):
        """
        Retorna uma representação do objeto em formato de dicionário.
        """
        return {
            'id': self.id,
            'tipo_termo': self.tipo_termo,
            'nome_usuario': self.nome_usuario,
            'cpf_usuario': self.cpf_usuario,
            'descricao_equipamento': self.descricao_equipamento,
            'nome_arquivo': self.nome_arquivo,
            'data_geracao': self.data_geracao.isoformat(),
            'gerado_por': self.gerado_por,
            'patrimonio': self.patrimonio,
            'estado_equipamento': self.estado_equipamento,
            'data_validade': self.data_validade.isoformat() if self.data_validade else None,
            # --- INÍCIO DA MUDANÇA ---
            'unidade_origem': self.unidade_origem,
            'unidade_destino': self.unidade_destino
            # --- FIM DA MUDANÇA ---
        }
