# 📄 Gerenciamento de Contratos

## ✅ Funcionalidade Implementada

Interface web completa para **gerenciar contratos de trabalho** dos funcionários, acessível para usuários **sem necessidade de acesso ao Admin**.

---

## 🎯 Como Usar

### **1. Visualizar Contratos**

Na página de detalhes do funcionário:
```
http://localhost:8000/funcionarios/{id}/
```

- Clique na aba **"Contratos"**
- Veja todos os contratos (ativos e inativos)
- Informações exibidas:
  - Tipo de Contrato (CLT, PJ, Estágio, etc.)
  - Data de Início
  - Data de Fim (ou "Indeterminado")
  - Carga Horária (horas/semana)
  - Status (Ativo/Inativo)

---

### **2. Cadastrar Novo Contrato**

**Opção A: Via Detalhes do Funcionário**
1. Acesse o funcionário
2. Aba **"Contratos"**
3. Clique em **"Novo Contrato"**
4. Preencha o formulário
5. Salve

**Opção B: Link Direto**
```
http://localhost:8000/funcionarios/{funcionario_id}/contratos/novo/
```

**Campos do Formulário:**
- **Tipo de Contrato*** (obrigatório)
- **Carga Horária*** (horas/semana, obrigatório)
- **Data de Início*** (obrigatório)
- **Data de Fim** (opcional - deixe em branco para prazo indeterminado)
- **Observações** (opcional)

---

### **3. Editar Contrato**

1. Acesse o funcionário → Aba "Contratos"
2. Clique em **"Editar"** na linha do contrato
3. Modifique os campos necessários
4. Salve

---

### **4. Excluir Contrato**

1. Acesse o funcionário → Aba "Contratos"
2. Clique em **"Excluir"** na linha do contrato
3. Confirme a exclusão

---

## 🔒 Validações Automáticas

### **1. Não permite períodos sobrepostos**
❌ **Erro:** "Já existe um contrato ativo para este funcionário neste período"

**Exemplo de erro:**
```
Contrato 1: 01/01/2024 até 31/12/2024
Contrato 2: 01/06/2024 até 31/12/2025 ← ERRO! Sobrepõe o Contrato 1
```

### **2. Data de fim não pode ser anterior à data de início**
❌ **Erro:** "Data de fim não pode ser anterior à data de início"

**Exemplo de erro:**
```
Data Início: 01/06/2024
Data Fim: 01/01/2024 ← ERRO!
```

### **3. Carga horária deve ser maior que zero**
❌ **Erro:** Deve ser no mínimo 1 hora/semana

---

## 📊 Tipos de Contrato

Configure os tipos no Admin:
```
http://localhost:8000/admin/core/tipocontrato/
```

**Exemplos comuns:**
- CLT (44h/semana)
- CLT Meio Período (22h/semana)
- PJ (Pessoa Jurídica)
- Estágio (20h ou 30h/semana)
- Temporário
- Aprendiz

---

## 💡 Casos de Uso

### **Caso 1: Contrato CLT Padrão**
```
Tipo: CLT
Carga Horária: 44
Data Início: 01/03/2024
Data Fim: [vazio] ← Prazo indeterminado
```

### **Caso 2: Estágio com Prazo Determinado**
```
Tipo: Estágio
Carga Horária: 20
Data Início: 01/02/2024
Data Fim: 31/01/2026 ← 2 anos
```

### **Caso 3: Renovação de Contrato**
```
Contrato Antigo:
- Data Início: 01/01/2023
- Data Fim: 31/12/2023

Novo Contrato:
- Data Início: 01/01/2024 ← Sem sobreposição
- Data Fim: 31/12/2024
```

---

## 🎨 Interface

### **Aba Contratos**
```
┌─────────────────────────────────────────────────┐
│ Contratos de Trabalho      [Novo Contrato]      │
├─────────────────────────────────────────────────┤
│ Tipo │ Início  │ Fim    │ Carga │ Status │ Ações│
├──────┼─────────┼────────┼───────┼────────┼──────┤
│ CLT  │01/03/24 │Indet.  │ 44h   │ Ativo  │Ed Ex │
│ PJ   │01/01/23 │28/02/24│ 40h   │Inativo │Ed Ex │
└─────────────────────────────────────────────────┘
```

### **Formulário**
```
┌─────────────────────────────────────────────────┐
│ Novo Contrato - João Silva                      │
├─────────────────────────────────────────────────┤
│ Tipo de Contrato*: [CLT ▼]                      │
│ Carga Horária*: [44] horas/semana               │
│ Data de Início*: [01/03/2024]                   │
│ Data de Fim: [ ] (opcional)                     │
│ Observações: [                                ] │
│              [                                ] │
│                                                  │
│                      [Cancelar] [Salvar Contrato]│
└─────────────────────────────────────────────────┘
```

---

## 🔧 Arquivos Criados/Modificados

### **Views (`funcionarios/views.py`)**
- `contrato_create()` - Criar contrato
- `contrato_update()` - Editar contrato
- `contrato_delete()` - Excluir contrato

### **URLs (`funcionarios/urls.py`)**
```python
path('<int:funcionario_pk>/contratos/novo/', views.contrato_create, name='contrato_create')
path('contratos/<int:pk>/editar/', views.contrato_update, name='contrato_update')
path('contratos/<int:pk>/excluir/', views.contrato_delete, name='contrato_delete')
```

### **Templates**
- `templates/funcionarios/contrato_form.html` - Formulário de contrato
- `templates/funcionarios/funcionario_detail.html` - Atualizado com botões e ações

### **Forms (`funcionarios/forms.py`)**
- `ContratoForm` - Ajustado para não exibir campo funcionário

---

## ✅ Benefícios

1. **Sem Admin**: Usuários regulares podem gerenciar contratos
2. **Validações**: Impede erros de sobreposição e datas inválidas
3. **Histórico**: Mantém registro de todos os contratos
4. **Rastreabilidade**: Sabe quando cada contrato começou/terminou
5. **Compliance**: Auxilia na gestão trabalhista

---

## 🚀 Próximos Passos (Sugestões)

- [ ] Notificações de vencimento de contrato
- [ ] Relatório de contratos a vencer
- [ ] Upload de documentos do contrato
- [ ] Assinatura digital
- [ ] Exportar contrato em PDF

---

**Sistema completo de gerenciamento de contratos implementado!** 🎉
