# ⚡ CONFIGURAR HIERARQUIA - GUIA RÁPIDO

## 🔴 Problema: Todos aparecem como "Alta Direção"

**Causa:** Os setores ainda não têm chefes definidos.

---

## ✅ SOLUÇÃO RÁPIDA (3 passos):

### **Opção 1: Via Script Interativo (RECOMENDADO)**

Execute no terminal:
```bash
python setup_hierarquia.py
```

O script vai:
1. ✅ Mostrar todos os setores e funcionários
2. ✅ Permitir que você escolha o chefe de cada setor
3. ✅ Configurar automaticamente

---

### **Opção 2: Via Admin Django**

#### **Passo 1: Acessar Admin**
```
http://localhost:8000/admin/
```

#### **Passo 2: Definir Chefes**
1. Clique em **"Core"** → **"Setores"**
2. Para cada setor, clique no nome
3. No campo **"Chefe do setor"**, selecione um funcionário
4. Clique em **"Salvar"**

**Exemplo:**
```
Setor: TI
Chefe do setor: [Selecione: João Silva - Diretor de TI]
[Salvar]

Setor: Financeiro  
Chefe do setor: [Selecione: Maria Santos - Diretora Financeira]
[Salvar]

Setor: RH
Chefe do setor: [Selecione: Pedro Costa - Gerente de RH]
[Salvar]
```

#### **Passo 3: Atualizar Hierarquia**
Execute no terminal:
```bash
python manage.py atualizar_hierarquia
```

Você verá algo como:
```
Iniciando atualização da hierarquia...

Processando setor: TI
  Chefe: João Silva
  ✓ 3 funcionário(s) atualizado(s)

Processando setor: Financeiro
  Chefe: Maria Santos
  ✓ 2 funcionário(s) atualizado(s)

==================================================
✓ Total de funcionários atualizados: 5
==================================================

Atualização concluída!
```

---

## 🔍 Verificar se funcionou:

### **1. Acesse o Organograma:**
```
http://localhost:8000/funcionarios/organograma/
```

### **2. Verifique um Funcionário:**
- Clique em qualquer funcionário
- Aba **"Informações"** deve mostrar o superior
- Aba **"Equipe"** (para chefes) mostra subordinados

---

## 📋 Estrutura Recomendada:

### **Para empresas pequenas:**
```
Alta Direção (sem setor/setor próprio)
├── Diretor Geral
│
Setores:
├── TI → Chefe: Diretor de TI
│   ├── Coordenador Dev
│   ├── Desenvolvedor A
│   └── Desenvolvedor B
│
├── Financeiro → Chefe: Diretor Financeiro
│   ├── Contador
│   └── Analista
│
└── RH → Chefe: Gerente de RH
    └── Assistente
```

### **Para empresas maiores:**
```
Crie mais setores e defina chefes:

Setor: Diretoria
Chefe: CEO

Setor: TI  
Chefe: Diretor de TI

Setor: Desenvolvimento
Chefe: Coordenador de Dev

Setor: Infraestrutura
Chefe: Coordenador de Infra

etc...
```

---

## ⚠️ Observações Importantes:

1. **Chefes também podem ter superior:**
   - O Diretor de TI pode ter como superior o CEO
   - Configure isso manualmente no Admin se necessário

2. **Alta Direção não tem superior:**
   - CEOs, Presidentes, Diretores Gerais
   - Não precisam de chefe de setor

3. **Novos funcionários:**
   - Já virão com superior automático ao selecionar o setor!

---

## 🆘 Problemas?

### Erro: "Nenhum setor cadastrado"
```bash
# Cadastre setores primeiro:
python setup_initial_data.py
```

### Erro ao executar comando:
```bash
# Certifique-se que está no ambiente virtual:
venv\Scripts\activate  # Windows

# E no diretório correto:
cd "c:\projetos\Folha de Pagamento Sonet 4.5"
```

### Hierarquia não aparece:
1. Verifique se definiu os chefes no Admin
2. Execute: `python manage.py atualizar_hierarquia`
3. Recarregue a página do organograma

---

## ✅ Checklist:

- [ ] Defini os chefes de cada setor no Admin
- [ ] Executei `python manage.py atualizar_hierarquia`
- [ ] Acessei o organograma e está correto
- [ ] Funcionários agora mostram seus superiores
- [ ] Chefes mostram seus subordinados na aba "Equipe"

---

**Depois de configurar, a hierarquia será automática para novos funcionários!** 🎉
