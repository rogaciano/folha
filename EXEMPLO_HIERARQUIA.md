# 📊 Exemplos Práticos de Hierarquia

## Exemplo 1: Estrutura Simples (Automática)

### **Configuração:**

**Setores e Chefes:**
```
Setor: TI
Chefe do Setor: João Silva (Diretor de TI)

Setor: Financeiro  
Chefe do Setor: Maria Santos (Diretora Financeira)
```

**Cadastrando Funcionários:**

```
Funcionário: Ana Costa
Função: Desenvolvedora
Setor: TI
Superior: [VAZIO] ← deixe em branco!

✅ Resultado: Superior = João Silva (automático!)
```

```
Funcionário: Pedro Lima
Função: Contador
Setor: Financeiro
Superior: [VAZIO] ← deixe em branco!

✅ Resultado: Superior = Maria Santos (automático!)
```

---

## Exemplo 2: Chefe de Setor com Superior

### **Problema:**
João Silva (Diretor de TI) é chefe do setor TI, mas responde ao CEO Carlos Oliveira.

### **Solução:**

```
Funcionário: João Silva
Função: Diretor de TI
Setor: TI
Superior: Carlos Oliveira ← preencha manualmente!

✅ Resultado: 
- João não será seu próprio superior
- João terá Carlos como superior
- Funcionários de TI continuam tendo João como superior automático
```

---

## Exemplo 3: Hierarquia Multi-Nível

### **Estrutura da Empresa:**

```
CEO: Carlos Oliveira
├── Diretor TI: João Silva
│   ├── Coordenador Dev: Ana Costa
│   │   ├── Desenvolvedor: Bruno Alves
│   │   └── Desenvolvedor: Carla Mendes
│   └── Analista Suporte: Pedro Lima
└── Diretora Financeira: Maria Santos
    ├── Contador: Paulo Souza
    └── Analista: Julia Ramos
```

### **Como Configurar:**

**1. Criar Setores:**
```
Setor: Diretoria → Chefe: [VAZIO]
Setor: TI → Chefe: João Silva
Setor: Desenvolvimento → Chefe: Ana Costa
Setor: Financeiro → Chefe: Maria Santos
```

**2. Cadastrar CEO (Alta Direção):**
```
Funcionário: Carlos Oliveira
Setor: Diretoria (ou qualquer setor sem chefe)
Superior: [VAZIO]

✅ Resultado: Alta direção (sem superior)
```

**3. Cadastrar Diretores:**
```
Funcionário: João Silva (Diretor TI)
Setor: TI
Superior: Carlos Oliveira ← manual, pois é chefe do setor

Funcionário: Maria Santos (Diretora Financeira)
Setor: Financeiro
Superior: Carlos Oliveira ← manual, pois é chefe do setor
```

**4. Cadastrar Coordenadora:**
```
Funcionário: Ana Costa (Coordenadora Dev)
Setor: Desenvolvimento
Superior: João Silva ← manual, pois é chefe do setor e responde a outra diretoria
```

**5. Cadastrar Funcionários Regulares:**
```
Funcionário: Bruno Alves
Setor: Desenvolvimento
Superior: [VAZIO]
✅ Superior automático = Ana Costa

Funcionário: Carla Mendes
Setor: Desenvolvimento
Superior: [VAZIO]
✅ Superior automático = Ana Costa

Funcionário: Pedro Lima
Setor: TI
Superior: [VAZIO]
✅ Superior automático = João Silva

Funcionário: Paulo Souza
Setor: Financeiro
Superior: [VAZIO]
✅ Superior automático = Maria Santos

Funcionário: Julia Ramos
Setor: Financeiro
Superior: [VAZIO]
✅ Superior automático = Maria Santos
```

---

## Exemplo 4: Funcionário de Um Setor Subordinado a Outro

### **Cenário:**
Rafael é do setor TI, mas responde diretamente ao Diretor Financeiro (por projeto especial).

### **Solução:**

```
Funcionário: Rafael Costa
Setor: TI
Superior: Maria Santos (Diretora Financeira) ← manual!

✅ Resultado: 
- Rafael está no setor TI
- Mas tem Maria (de outro setor) como superior
- Automação é sobrescrita pela definição manual
```

---

## Resumo Visual

### **Regra de Ouro:**

```
┌─────────────────────────────────────────────┐
│  Campo "Superior" está PREENCHIDO?          │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
      SIM              NÃO
       │                │
       ▼                ▼
  Usa o superior    Usa o chefe
  definido          do setor
  manualmente       automaticamente
       │                │
       └────────┬───────┘
                │
                ▼
          Superior Final
```

---

## 💡 Dicas Práticas

### ✅ **Use Automação Para:**
- Funcionários regulares (não-gestores)
- Estruturas simples de setor
- Manter consistência

### ✏️ **Use Manual Para:**
- Chefes de setor (que respondem a outra diretoria)
- Casos especiais (subordinação cruzada)
- Estruturas matriciais
- Alta direção (deixe vazio)

---

## 🔄 Fluxo de Trabalho

**Para 95% dos funcionários:**
1. Selecione o Setor
2. Deixe Superior em branco
3. Salve
4. ✅ Pronto! Superior definido automaticamente

**Para chefes/exceções (5%):**
1. Selecione o Setor
2. Preencha o Superior manualmente
3. Salve
4. ✅ Pronto! Superior customizado

---

**Com essa flexibilidade, você tem o melhor dos dois mundos: automação + controle manual quando necessário!** 🎉
