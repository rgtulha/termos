from app import db
from datetime import datetime

class Termo(db.Model):
    """
    Modelo PAI. Armazena os dados principais do termo.
    (Modificado para a arquitetura Um-para-Muitos)
    """
    __tablename__ = 'termos'

    id = db.Column(db.Integer, primary_key=True)
    tipo_termo = db.Column(db.String(100), nullable=False)
    nome_usuario = db.Column(db.String(255), nullable=False)
    cpf_usuario = db.Column(db.String(14), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False, unique=True)
    data_geracao = db.Column(db.DateTime, default=datetime.utcnow)
    gerado_por = db.Column(db.String(100)) 
    data_validade = db.Column(db.Date, nullable=True)
    unidade_origem = db.Column(db.String(100), nullable=True)
    unidade_destino = db.Column(db.String(100), nullable=True)

    # --- INÍCIO DA MUDANÇA ---
    # Colunas REMOVIDAS daqui:
    # - descricao_equipamento
    # - patrimonio
    # - estado_equipamento

    # NOVA Relação:
    # Isto liga o Termo aos seus Itens.
    # 'cascade' garante que, se um Termo for apagado, os seus itens também o são.
    itens = db.relationship('ItemEquipamento', backref='termo', lazy=True, cascade="all, delete-orphan")
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
            'nome_arquivo': self.nome_arquivo,
            'data_geracao': self.data_geracao.isoformat(),
            'gerado_por': self.gerado_por,
            'data_validade': self.data_validade.isoformat() if self.data_validade else None,
            'unidade_origem': self.unidade_origem,
            'unidade_destino': self.unidade_destino,
            
            # --- INÍCIO DA MUDANÇA ---
            # O 'to_dict()' agora também pode incluir os seus itens:
            'itens': [item.to_dict() for item in self.itens]
            # --- FIM DA MUDANÇA ---
        }
