# 🚀 Guia de Início Rápido

## ⚡ Instalação em 5 Minutos (Windows)

```powershell
# 1. Navegue até o projeto
cd "c:\projetos\Folha de Pagamento Sonet 4.5"

# 2. Crie o ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Instale dependências
pip install -r requirements.txt

# 4. Execute migrações
python manage.py migrate

# 5. Crie superusuário
python manage.py createsuperuser

# 6. Crie dados iniciais
python setup_initial_data.py

# 7. Inicie o servidor
python manage.py runserver
```

Acesse: **http://localhost:8000**

Admin: **http://localhost:8000/admin**

## 🎯 Primeiro Uso

1. Cadastre funcionários no admin
2. Crie contratos para os funcionários
3. Gere a folha de pagamento
4. Explore o dashboard

Consulte o [README.md](README.md) para mais detalhes!
