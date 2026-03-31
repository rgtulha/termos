import ldap
import re
from flask import current_app

class ADIntegration:
    """
    Classe para lidar com a integração com o Active Directory.
    (Busca CPF no campo 'physicalDeliveryOfficeName' e valida completamente)
    """
    def __init__(self):
        self.server = current_app.config['AD_SERVER']
        self.port = current_app.config['AD_PORT']
        self.base_dn = current_app.config['AD_BASE_DN']
        self.user_dn = current_app.config['AD_USER_DN']
        self.password = current_app.config['AD_PASSWORD']
        
        self.search_filter_template = '(&(objectClass=user)(cn={0}*))'
        
        self.attributes = ['cn', 'physicalDeliveryOfficeName', 'sAMAccountName'] 
        
        self.conn = None

    def _validar_cpf(self, cpf_bruto: str) -> str:
        """
        Realiza a validação completa de um CPF, verificando o formato,
        comprimento, dígitos repetidos e os dígitos verificadores.
        
        :param cpf_bruto: CPF no formato 'XXX.XXX.XXX-XX', 'XXXXXXXXXXX' ou com outros caracteres.
        :return: O CPF limpo (apenas números) se for válido, ou 'CPF INCORRETO !!!' caso contrário.
        """
        MSG_ERRO = "CPF INCORRETO !!!"

        # 1. Se estiver vazio ou não for uma string, retorna erro
        if not isinstance(cpf_bruto, str) or not cpf_bruto.strip():
            return MSG_ERRO

        # 2. Remover caracteres não numéricos do CPF
        cpf_limpo = re.sub(r'\D', '', cpf_bruto)

        # 3. Verificar se o CPF tem 11 dígitos após a limpeza
        if len(cpf_limpo) != 11:
            return MSG_ERRO

        # 4. Verificar se todos os dígitos são iguais (ex: 11111111111)
        # CPFs com dígitos repetidos são inválidos de acordo com a regra da Receita Federal.
        if cpf_limpo == cpf_limpo[0] * 11:
            return MSG_ERRO

        # 5. Calcular o primeiro dígito verificador
        soma = 0
        for i in range(9):
            soma += int(cpf_limpo[i]) * (10 - i)
        
        primeiro_digito_calc = 11 - (soma % 11)
        if primeiro_digito_calc > 9:
            primeiro_digito_calc = 0

        # 6. Calcular o segundo dígito verificador
        soma = 0
        for i in range(10): # Agora inclui o primeiro dígito verificador para o cálculo
            soma += int(cpf_limpo[i]) * (11 - i)
            
        segundo_digito_calc = 11 - (soma % 11)
        if segundo_digito_calc > 9:
            segundo_digito_calc = 0

        # 7. Comparar os dígitos calculados com os dígitos fornecidos no CPF
        if int(cpf_limpo[9]) == primeiro_digito_calc and \
           int(cpf_limpo[10]) == segundo_digito_calc:
            return cpf_limpo # Retorna o CPF limpo (apenas números)
        else:
            return MSG_ERRO

    def _connect(self):
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        try:
            self.conn = ldap.initialize(f"ldap://{self.server}:{self.port}")
            self.conn.protocol_version = ldap.VERSION3
            self.conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 5.0)
            self.conn.simple_bind_s(self.user_dn, self.password)
            return True
        except ldap.INVALID_CREDENTIALS:
            print("Erro de BIND: Credenciais inválidas.")
            return False
        except ldap.SERVER_DOWN:
            print(f"Erro de Conexão: Servidor não encontrado ({self.server}:{self.port}).")
            return False
        except ldap.LDAPError as e:
            print(f"Erro LDAP ao conectar: {e}")
            return False

    def _disconnect(self):
        if self.conn:
            self.conn.unbind_s()

    def search_users(self, partial_name):
        if not self._connect():
            return None

        search_filter = self.search_filter_template.format(partial_name)
        
        try:
            results = self.conn.search_s(self.base_dn, ldap.SCOPE_SUBTREE, search_filter, self.attributes)
            
            if not results:
                return [] 

            user_list = []
            for dn, entry in results:
                user_data = {}
                for attr in self.attributes:
                    if attr in entry:
                        try:
                            user_data[attr] = entry[attr][0].decode('utf-8')
                        except Exception:
                            user_data[attr] = str(entry[attr][0])
                    else:
                        user_data[attr] = ''
                
                # 1. Pega o valor do atributo correto
                raw_cpf = user_data.get('physicalDeliveryOfficeName', '')
                
                # 2. Aplica a validação COMPLETA
                cpf_validado = self._validar_cpf(raw_cpf)

                mapped_data = {
                    'nome_completo': user_data.get('cn', ''),
                    'cpf': cpf_validado, 
                    'login': user_data.get('sAMAccountName', '')
                }
                user_list.append(mapped_data)
            
            return user_list

        except ldap.LDAPError as e:
            print(f"Erro ao executar a busca LDAP: {e}")
            return None 
        finally:
            self._disconnect()

