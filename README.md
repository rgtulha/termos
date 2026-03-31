# Sistema de Geração de Termos AGEHAB

Este é um sistema web para a geração automatizada de termos de responsabilidade, utilizando modelos DOCX e integração com o Active Directory.

## Requisitos de Sistema

- **Sistema Operacional:** CentOS 9 Stream
- **Servidor Web:** Nginx
- **Servidor de Aplicação WSGI:** Gunicorn
- **Banco de Dados:** MySQL 8.x
- **Backend:** Python 3.9+
- **Frontend:** HTML5, CSS3, JavaScript

---

## Guia de Preparação do Servidor e Implantação (CentOS 9)

Siga os passos abaixo para configurar um servidor CentOS 9 do zero e implantar a aplicação.

### 1. Atualização do Sistema

Primeiro, atualize todos os pacotes do sistema para a versão mais recente.

```bash
sudo dnf update -y
sudo dnf upgrade -y
```

### 2. Instalação de Dependências Essenciais

Instale o repositório EPEL (Extra Packages for Enterprise Linux) e outras ferramentas de desenvolvimento necessárias.

```bash
sudo dnf install -y epel-release
sudo dnf install -y git python3-devel gcc mysql-devel curl
```

### 3. Instalação e Configuração do Banco de Dados MySQL

O sistema utilizará o MySQL para armazenar metadados dos termos gerados.

```bash
# Instalar o servidor MySQL
sudo dnf install -y mysql-server

# Iniciar e habilitar o serviço do MySQL
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Executar o script de segurança para definir a senha do root e outras configurações
sudo mysql_secure_installation
```

Após a instalação segura, crie o banco de dados e um usuário para a aplicação.

```sql
-- Conecte-se ao MySQL como root
sudo mysql -u root -p

-- Crie o banco de dados
CREATE DATABASE termos_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crie um usuário e conceda as permissões (substitua 'sua_senha_segura')
CREATE USER 'termos_user'@'localhost' IDENTIFIED BY 'sua_senha_segura';
GRANT ALL PRIVILEGES ON termos_db.* TO 'termos_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Instalação do Python e Criação do Ambiente Virtual

Vamos garantir que o Python 3.9 (padrão no CentOS 9) e o `pip` estejam instalados.

```bash
sudo dnf install -y python3 python3-pip
```

Agora, clone o projeto e configure o ambiente virtual.

```bash
# Navegue para o diretório onde deseja clonar o projeto
cd /var/www

# Clone o repositório (substitua pela URL correta do seu repositório)
git clone https://github.com/rgtulha/TermosAgehab.git
cd TermosAgehab

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências do projeto
pip install -r requirements.txt
```

### 5. Instalação e Configuração do Gunicorn

Gunicorn será o nosso servidor de aplicação WSGI.

```bash
pip install gunicorn
```

### 6. Instalação e Configuração do Nginx

Nginx atuará como um proxy reverso, recebendo as requisições HTTP e encaminhando-as para o Gunicorn.

```bash
# Instalar o Nginx
sudo dnf install -y nginx

# Iniciar e habilitar o serviço
sudo systemctl start nginx
sudo systemctl enable nginx
```

Crie um arquivo de configuração para o nosso site:

```bash
sudo nano /etc/nginx/conf.d/termosagehab.conf
```

Cole o seguinte conteúdo no arquivo, ajustando `server_name` para o seu domínio ou endereço IP:

```nginx
server {
    listen 80;
    server_name seu_dominio_ou_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/TermosAgehab/static;
    }
}
```

Verifique a sintaxe do Nginx e reinicie o serviço:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Configuração do Firewall

Permita o tráfego HTTP e HTTPS através do firewall.

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 8. Executando a Aplicação

Agora você pode iniciar a aplicação manualmente com o Gunicorn para testar:

```bash
# Certifique-se de que seu ambiente virtual está ativado
source /var/www/TermosAgehab/venv/bin/activate

# Inicie o Gunicorn
gunicorn --workers 3 --bind unix:termosagehab.sock -m 007 wsgi:app
```
> **Nota:** Você precisará criar um arquivo `wsgi.py` para apontar para a sua instância da aplicação Flask.

Para produção, é recomendado criar um serviço `systemd` para gerenciar o processo do Gunicorn automaticamente.

---
Este guia cobre todos os passos essenciais para colocar o ambiente em produção. O próximo passo é desenvolver o código da aplicação.
