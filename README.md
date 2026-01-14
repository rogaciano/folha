# Sistema de Folha de Pagamento - Sonet 4.5

Sistema completo de controle gerencial de folha de pagamento desenvolvido em Django, com foco em usabilidade (UX/UI), eficiência operacional e aderência às melhores práticas de desenvolvimento.

## 🚀 Stack Tecnológica

- **Backend**: Django 4.2.7 (Python 3.11)
- **Frontend**: Alpine.js + Tailwind CSS
- **Banco de Dados**: 
  - SQLite (Desenvolvimento)
  - PostgreSQL (Produção)
- **Containerização**: Docker + Docker Compose
- **Servidor**: Gunicorn + Nginx

## 📋 Funcionalidades

### Módulos Principais

1. **Gestão de Funcionários**
   - Cadastro completo de funcionários com validação de CPF
   - Controle de contratos (CLT, Estágio, PJ, etc.)
   - Gerenciamento de lançamentos fixos (proventos/descontos recorrentes)
   - Controle de férias com cálculo automático de períodos aquisitivos
   - Histórico completo de adiantamentos

2. **Folha de Pagamento**
   - Geração automática de folha mensal
   - Lançamento automático de salário base
   - Aplicação de lançamentos fixos ativos
   - Desconto automático de adiantamentos pendentes
   - Controle de status (Rascunho, Fechada, Paga)
   - Resumo por funcionário com totalizadores

3. **Adiantamentos**
   - Lançamento individual
   - Lançamento massivo com filtros (setor, função, status)
   - Opções de valor fixo ou percentual do salário

4. **Dashboard Gerencial**
   - Estatísticas de funcionários (ativos, inativos, em férias)
   - Alertas de férias a vencer (60 dias)
   - Admissões recentes
   - Última folha processada

## 🛠️ Instalação e Configuração

### Pré-requisitos

- Python 3.11+
- pip
- virtualenv (recomendado)
- Docker e Docker Compose (para produção)

### Configuração de Desenvolvimento

1. **Clone o repositório**
```bash
cd "c:\projetos\Folha de Pagamento Sonet 4.5"
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instale as dependências**
```bash
pip install -r requirements.txt
```

5. **Configure as variáveis de ambiente**
```bash
# Copie o arquivo de exemplo
copy .env.example .env

# Edite o arquivo .env com suas configurações
```

6. **Execute as migrações**
```bash
python manage.py migrate
```

7. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

8. **Crie dados iniciais (opcional)**
```bash
python manage.py shell
```

Execute no shell Python:
```python
from core.models import Setor, Funcao, TipoContrato, ProventoDesconto

# Setores
Setor.objects.create(nome='Tecnologia', descricao='Departamento de TI')
Setor.objects.create(nome='Recursos Humanos', descricao='RH')
Setor.objects.create(nome='Financeiro', descricao='Finanças')

# Funções
Funcao.objects.create(nome='Desenvolvedor', nivel_salarial_referencia=5000.00)
Funcao.objects.create(nome='Analista', nivel_salarial_referencia=4000.00)
Funcao.objects.create(nome='Gerente', nivel_salarial_referencia=8000.00)

# Tipos de Contrato
TipoContrato.objects.create(nome='CLT', descricao='Consolidação das Leis do Trabalho')
TipoContrato.objects.create(nome='Estágio', descricao='Contrato de Estágio')
TipoContrato.objects.create(nome='PJ', descricao='Pessoa Jurídica')

# Proventos e Descontos
ProventoDesconto.objects.create(
    nome='Salário Base',
    codigo_referencia='SALARIO',
    tipo='P',
    impacto='F',
    descricao='Salário base do funcionário'
)

ProventoDesconto.objects.create(
    nome='Vale Transporte',
    codigo_referencia='VT',
    tipo='P',
    impacto='F',
    descricao='Vale transporte'
)

ProventoDesconto.objects.create(
    nome='INSS',
    codigo_referencia='INSS',
    tipo='D',
    impacto='P',
    descricao='Desconto do INSS'
)

ProventoDesconto.objects.create(
    nome='Adiantamento Salarial',
    codigo_referencia='ADIANTAMENTO',
    tipo='D',
    impacto='F',
    descricao='Desconto de adiantamento'
)
```

9. **Inicie o servidor de desenvolvimento**
```bash
python manage.py runserver
```

Acesse: http://localhost:8000

### Configuração com Docker (Desenvolvimento)

```bash
docker-compose -f docker-compose.dev.yml up --build
```

Acesse: http://localhost:8000

## 🐳 Deploy em Produção com Docker

### 1. Configure as variáveis de ambiente

Crie um arquivo `.env` com as seguintes variáveis:

```env
SECRET_KEY=sua-chave-secreta-super-segura
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=folha_pagamento
DB_USER=postgres
DB_PASSWORD=senha-segura-do-banco
DB_HOST=db
DB_PORT=5432
```

### 2. Execute o Docker Compose

```bash
docker-compose up -d --build
```

### 3. Execute as migrações

```bash
docker-compose exec web python manage.py migrate
```

### 4. Crie um superusuário

```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Colete arquivos estáticos

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

O sistema estará disponível em http://localhost (porta 80)

## 🧪 Executando Testes

### Com pytest

```bash
pytest
```

### Com coverage

```bash
pytest --cov=. --cov-report=html
```

O relatório HTML será gerado em `htmlcov/index.html`

### Testes individuais por app

```bash
# Core
pytest core/tests.py

# Funcionários
pytest funcionarios/tests.py

# Folha
pytest folha/tests.py
```

## 📁 Estrutura do Projeto

```
folha-pagamento/
├── config/                      # Configurações do projeto
│   ├── settings/
│   │   ├── base.py             # Configurações base
│   │   ├── development.py      # Configurações de desenvolvimento
│   │   └── production.py       # Configurações de produção
│   ├── urls.py                 # URLs principais
│   ├── wsgi.py                 # WSGI para produção
│   └── asgi.py                 # ASGI para async
├── core/                        # App principal (dados mestres)
│   ├── models.py               # Setor, Função, TipoContrato, ProventoDesconto
│   ├── views.py                # Dashboard
│   ├── admin.py                # Admin do Django
│   └── tests.py                # Testes
├── funcionarios/                # App de funcionários
│   ├── models.py               # Funcionario, Contrato, LancamentoFixo, etc.
│   ├── views.py                # CRUD de funcionários
│   ├── forms.py                # Formulários
│   ├── admin.py                # Admin do Django
│   └── tests.py                # Testes
├── folha/                       # App de folha de pagamento
│   ├── models.py               # FolhaPagamento, ItemFolha
│   ├── views.py                # Visualização e geração de folha
│   ├── forms.py                # Formulários
│   ├── services.py             # Lógica de negócio
│   ├── admin.py                # Admin do Django
│   └── tests.py                # Testes
├── templates/                   # Templates HTML
│   ├── base.html               # Template base
│   ├── core/                   # Templates do core
│   ├── funcionarios/           # Templates de funcionários
│   └── folha/                  # Templates de folha
├── static/                      # Arquivos estáticos
├── media/                       # Arquivos de mídia
├── Dockerfile                   # Dockerfile para produção
├── Dockerfile.dev              # Dockerfile para desenvolvimento
├── docker-compose.yml          # Docker Compose produção
├── docker-compose.dev.yml      # Docker Compose desenvolvimento
├── nginx.conf                  # Configuração do Nginx
├── requirements.txt            # Dependências Python
├── manage.py                   # Gerenciador Django
├── pytest.ini                  # Configuração do pytest
└── README.md                   # Este arquivo
```

## 🎨 Interface do Usuário

O sistema utiliza **Tailwind CSS** para estilização e **Alpine.js** para interatividade, proporcionando:

- Design responsivo (mobile-first)
- Interface moderna e limpa
- Componentes reutilizáveis
- Validação de formulários em tempo real
- Feedback visual para ações do usuário
- Modais e dropdowns interativos

## 🔐 Segurança

O sistema implementa as melhores práticas de segurança:

- Proteção CSRF ativada
- Proteção contra XSS
- Validação de dados de entrada
- Senhas hasheadas com PBKDF2
- Configurações separadas para dev/prod
- HTTPS obrigatório em produção
- Validação de CPF

## 📊 Fluxo de Trabalho

### Geração de Folha de Pagamento

1. Acesse **Folha de Pagamento** > **Gerar Nova Folha**
2. Selecione o mês e ano
3. O sistema automaticamente:
   - Identifica contratos ativos no período
   - Lança salário base de cada funcionário
   - Aplica lançamentos fixos ativos
   - Desconta adiantamentos pendentes
4. Revise os itens gerados
5. Adicione itens manuais se necessário
6. Feche a folha quando estiver correta
7. Marque como paga após o pagamento

### Lançamento de Adiantamentos em Massa

1. Acesse **Adiantamentos** > **Lançamento Massivo**
2. Configure os filtros (setor, função, status)
3. Escolha entre valor fixo ou percentual
4. Confirme o lançamento
5. Os adiantamentos serão descontados automaticamente na próxima folha

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto foi desenvolvido para fins educacionais e comerciais.

## 👥 Suporte

Para suporte, entre em contato através de:
- Email: suporte@sonet.com.br
- Telefone: (11) 1234-5678

## 🔄 Changelog

### Versão 4.5 (2024)
- ✅ Sistema completo de folha de pagamento
- ✅ Gestão de funcionários e contratos
- ✅ Lançamentos fixos e adiantamentos
- ✅ Controle de férias
- ✅ Dashboard gerencial
- ✅ Testes unitários
- ✅ Docker para dev/prod
- ✅ Interface moderna com Alpine.js e Tailwind CSS

## 🚧 Roadmap

- [ ] Relatórios em PDF
- [ ] Exportação para Excel
- [ ] Integração com sistemas contábeis
- [ ] Cálculo automático de INSS e IRRF
- [ ] Controle de ponto eletrônico
- [ ] API REST completa
- [ ] App mobile
- [ ] Notificações por e-mail
- [ ] Assinatura digital de recibos
- [ ] Multi-empresa

---

**Desenvolvido com ❤️ por Sonet - Sistema de Folha de Pagamento v4.5**
