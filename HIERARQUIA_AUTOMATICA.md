# 🔄 Hierarquia Automática por Setor

## ✨ Como Funciona

**Lógica Inteligente:**
1. ✅ Se o campo **"Superior/Responsável"** estiver **preenchido** → usa o superior definido manualmente
2. ✅ Se o campo **"Superior/Responsável"** estiver **vazio** → usa o chefe do setor automaticamente
3. ✅ Chefe do setor **nunca** será seu próprio superior

**Flexível**: Permite exceções (ex: chefe de setor que responde a outra diretoria) sem perder a automação para funcionários regulares!

---

## 🎯 Configuração

### Passo 1: Definir Chefes de Setor

1. Acesse o **Admin Django**: http://localhost:8000/admin/
2. Vá em **Core → Setores**
3. Para cada setor, selecione o **"Chefe do Setor"**
4. Salve

**Exemplo:**
```
Setor: TI
Chefe do Setor: João Silva (Diretor de TI)

Setor: Financeiro
Chefe do Setor: Maria Santos (Diretora Financeira)

Setor: RH
Chefe do Setor: Pedro Costa (Gerente de RH)
```

### Passo 2: Atualizar Hierarquia Automaticamente

Execute o comando:
```bash
python manage.py atualizar_hierarquia
```

Este comando irá:
- ✅ Percorrer todos os setores com chefe definido
- ✅ Definir o chefe como superior de todos os funcionários do setor
- ✅ Mostrar um relatório do que foi atualizado

**Para forçar atualização (sobrescrever hierarquia existente):**
```bash
python manage.py atualizar_hierarquia --force
```

---

## 🤖 Automação via Signals

**Novos funcionários são automaticamente configurados!**

Quando você **cadastrar um novo funcionário**:
1. Selecione o **Setor**
2. O sistema **automaticamente define** o chefe daquele setor como superior
3. Não precisa fazer mais nada!

**Quando alterar o chefe de um setor:**
- Todos os funcionários sem superior serão atualizados automaticamente

---

## 📋 Exemplos de Uso

### Exemplo 1: Estrutura Simples

**Setores:**
```
TI → Chefe: João (Diretor TI)
Financeiro → Chefe: Maria (Diretora)
Comercial → Chefe: Carlos (Gerente)
```

**Funcionários:**
```
Setor TI:
├── João (Diretor) ← Chefe, sem superior (alta direção)
├── Ana (Desenvolvedora) ← Superior: João
├── Bruno (Analista) ← Superior: João
└── Carla (Suporte) ← Superior: João

Setor Financeiro:
├── Maria (Diretora) ← Chefe, sem superior (alta direção)
├── Paulo (Contador) ← Superior: Maria
└── Julia (Analista) ← Superior: Maria
```

### Exemplo 2: Hierarquia Multi-Nível

Se você quiser uma hierarquia mais complexa, pode criar **subsetores**:

```
Setor: TI
Chefe: João (CTO)

Setor: Desenvolvimento (dentro de TI)
Chefe: Ana (Coordenadora)

Setor: Infraestrutura (dentro de TI)
Chefe: Bruno (Coordenador)
```

Ou pode definir manualmente no Admin se preferir uma estrutura diferente.

---

## 🔍 Verificando a Hierarquia

### 1. Via Organograma
Acesse: http://localhost:8000/funcionarios/organograma/

- **Visão Hierárquica**: Mostra a árvore completa
- **Visão por Setores**: Mostra funcionários agrupados por setor

### 2. Via Detalhes do Funcionário
Acesse qualquer funcionário e veja a aba **"Equipe"**:
- Cadeia hierárquica superior
- Lista de subordinados diretos

---

## ⚙️ Lógica Técnica

### Signals Implementados:

**1. `pre_save` - Antes de salvar funcionário:**
```python
- Se o funcionário NÃO tem superior definido
- E o setor tem um chefe
- Então: Define o chefe como superior automaticamente
```

**2. `post_save` - Depois de definir chefe de setor:**
```python
- Quando um funcionário vira chefe de setor
- Atualiza todos os funcionários daquele setor
- Define ele como superior (se não tiverem superior)
```

### Comando de Gestão:

```bash
python manage.py atualizar_hierarquia
```

**Opções:**
- `--force`: Sobrescreve hierarquia existente (cuidado!)

---

## 🎨 Vantagens desta Abordagem

✅ **Simples**: Apenas defina o chefe de cada setor
✅ **Automático**: Novos funcionários já vêm configurados
✅ **Escalável**: Funciona para empresas de qualquer tamanho
✅ **Flexível**: Pode sobrescrever manualmente se necessário
✅ **Visual**: Organograma gerado automaticamente

---

## 📊 Casos Especiais

### Funcionário sem setor com chefe:
- Não terá superior automático
- Considerado alta direção

### Chefe de setor em outro setor:
- Pode ser chefe de um setor e funcionário de outro
- Exemplo: Coordenador de TI (chefe de Desenvolvimento, mas subordinado ao Diretor de TI)

### Hierarquia manual:
- Se você definir o superior manualmente no Admin
- O sistema respeita sua escolha
- Não sobrescreve automaticamente

---

## 🚀 Fluxo de Trabalho Recomendado

**Para uma nova empresa:**

1. **Criar Setores**
   - Cadastre todos os departamentos

2. **Cadastrar Direção**
   - Cadastre os diretores/presidência
   - Não defina setor ou defina setor específico "Direção"

3. **Definir Chefes**
   - Para cada setor, defina quem é o chefe

4. **Cadastrar Funcionários**
   - Adicione os demais funcionários
   - Hierarquia será automática!

5. **Verificar**
   - Acesse o organograma
   - Confira se está correto

---

## 🔧 Manutenção

### Trocar chefe de setor:
1. Edite o setor no Admin
2. Selecione o novo chefe
3. Execute: `python manage.py atualizar_hierarquia --force`

### Reorganizar departamentos:
1. Altere os setores dos funcionários
2. Execute: `python manage.py atualizar_hierarquia`

---

## ✅ Status

- ✅ Signals implementados e ativos
- ✅ Comando de gestão pronto
- ✅ Hierarquia automática funcionando
- ✅ Organograma visual disponível

**Pronto para uso!** 🎉
