# Guia de Instalação Detalhado

Este documento fornece instruções passo a passo para instalação do Sistema de Folha de Pagamento.

## Instalação em Windows

### 1. Instalar Python 3.11+

1. Baixe o Python em https://www.python.org/downloads/
2. Execute o instalador
3. **IMPORTANTE**: Marque a opção "Add Python to PATH"
4. Clique em "Install Now"

Verifique a instalação:
```powershell
python --version
```

### 2. Instalar Git (opcional)

1. Baixe em https://git-scm.com/download/win
2. Execute o instalador com as opções padrão

### 3. Configurar o Projeto

Abra o PowerShell e navegue até o diretório do projeto:

```powershell
cd "c:\projetos\Folha de Pagamento Sonet 4.5"
```

Crie um ambiente virtual:
```powershell
python -m venv venv
```

Ative o ambiente virtual:
```powershell
.\venv\Scripts\Activate.ps1
```

Se houver erro de execução de scripts, execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Instale as dependências:
```powershell
pip install -r requirements.txt
```

### 4. Configurar o Banco de Dados

Copie o arquivo de exemplo:
```powershell
copy .env.example .env
```

Execute as migrações:
```powershell
python manage.py migrate
```

### 5. Criar Superusuário

```powershell
python manage.py createsuperuser
```

Preencha os dados solicitados:
- Username
- Email
- Password

### 6. Criar Dados Iniciais

Execute o script de dados iniciais:
```powershell
python manage.py shell
```

Copie e cole o código Python do README para criar setores, funções, etc.

### 7. Iniciar o Servidor

```powershell
python manage.py runserver
```

Acesse: http://localhost:8000

---

## Instalação em Linux/Ubuntu

### 1. Atualizar o Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Instalar Python e Dependências

```bash
sudo apt install python3.11 python3.11-venv python3-pip -y
```

### 3. Clonar ou Navegar até o Projeto

```bash
cd /caminho/para/o/projeto
```

### 4. Criar Ambiente Virtual

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 5. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 6. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
nano .env  # Edite conforme necessário
```

### 7. Executar Migrações

```bash
python manage.py migrate
```

### 8. Criar Superusuário

```bash
python manage.py createsuperuser
```

### 9. Iniciar o Servidor

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## Instalação com Docker

### Windows

1. Instale o Docker Desktop: https://www.docker.com/products/docker-desktop

2. Navegue até o diretório do projeto:
```powershell
cd "c:\projetos\Folha de Pagamento Sonet 4.5"
```

3. Para desenvolvimento:
```powershell
docker-compose -f docker-compose.dev.yml up --build
```

4. Para produção:
```powershell
# Configure o .env primeiro
docker-compose up -d --build

# Execute migrações
docker-compose exec web python manage.py migrate

# Crie superusuário
docker-compose exec web python manage.py createsuperuser
```

### Linux

1. Instale o Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

2. Instale o Docker Compose:
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. Execute os comandos Docker listados acima para Windows

---

## Configuração de Produção

### 1. Configurar PostgreSQL

#### Windows
1. Baixe o PostgreSQL: https://www.postgresql.org/download/windows/
2. Instale com as configurações padrão
3. Anote a senha do usuário postgres

#### Linux
```bash
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres psql
```

No psql:
```sql
CREATE DATABASE folha_pagamento;
CREATE USER folha_user WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE folha_pagamento TO folha_user;
\q
```

### 2. Configurar o .env para Produção

```env
SECRET_KEY=gere-uma-chave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=folha_pagamento
DB_USER=folha_user
DB_PASSWORD=senha_segura
DB_HOST=localhost
DB_PORT=5432
```

### 3. Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 4. Configurar Gunicorn

Crie um arquivo `gunicorn_config.py`:
```python
bind = "0.0.0.0:8000"
workers = 4
timeout = 120
```

Inicie o Gunicorn:
```bash
gunicorn --config gunicorn_config.py config.wsgi:application
```

### 5. Configurar Nginx (Opcional)

Instale o Nginx:
```bash
sudo apt install nginx -y
```

Crie um arquivo de configuração:
```bash
sudo nano /etc/nginx/sites-available/folha
```

Conteúdo:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location /static/ {
        alias /caminho/para/staticfiles/;
    }

    location /media/ {
        alias /caminho/para/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Ative o site:
```bash
sudo ln -s /etc/nginx/sites-available/folha /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Solução de Problemas

### Erro: ModuleNotFoundError

**Problema**: Módulo não encontrado ao iniciar o servidor

**Solução**:
```bash
# Certifique-se de estar no ambiente virtual
pip install -r requirements.txt
```

### Erro: OperationalError at /

**Problema**: Erro ao acessar o banco de dados

**Solução**:
```bash
python manage.py migrate
```

### Erro: CSRF verification failed

**Problema**: Token CSRF inválido

**Solução**: Limpe os cookies do navegador ou adicione o domínio em CSRF_TRUSTED_ORIGINS no settings

### Porta 8000 já em uso

**Problema**: Outra aplicação está usando a porta 8000

**Solução**:
```bash
# Use outra porta
python manage.py runserver 8001

# Ou mate o processo na porta 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID [PID_NUMBER] /F

# Linux
lsof -ti:8000 | xargs kill -9
```

---

## Próximos Passos

Após a instalação, consulte o [README.md](README.md) para:
- Criar dados iniciais (setores, funções, etc.)
- Entender o fluxo de trabalho
- Aprender a usar o sistema

Para suporte adicional, contate: suporte@sonet.com.br
