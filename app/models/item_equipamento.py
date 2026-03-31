from app import db

class ItemEquipamento(db.Model):
    """
    Novo Modelo FILHO.
    Armazena cada equipamento individual associado a um Termo.
    """
    __tablename__ = 'item_equipamentos'

    id = db.Column(db.Integer, primary_key=True)
    
    # As colunas que estavam no Termo, agora estão aqui:
    descricao = db.Column(db.String(255), nullable=False)
    patrimonio = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(100), nullable=True)

    # --- A Ligação (Chave Estrangeira) ---
    # Esta coluna diz a qual 'Termo' (pai) este item pertence.
    # 'termos.id' refere-se à tabela 'termos' e à coluna 'id'.
    termo_id = db.Column(db.Integer, db.ForeignKey('termos.id'), nullable=False)
    # --- FIM DA LIGAÇÃO ---

    def __repr__(self):
        return f"<ItemEquipamento {self.id} - {self.descricao}>"

    def to_dict(self):
        """
        Retorna uma representação do item em formato de dicionário.
        """
        return {
            'id': self.id,
            'descricao': self.descricao,
            'patrimonio': self.patrimonio,
            'estado': self.estado,
            'termo_id': self.termo_id
        }
