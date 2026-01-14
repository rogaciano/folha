# 🎨 Melhoria: Campo Tipo de Valor em Lançamentos Fixos

## 📋 Alteração Implementada

O formulário de **Lançamentos Fixos** agora possui um campo separado e explícito para escolher o **Tipo de Valor**, seguindo o mesmo padrão visual e funcional do formulário de **Adiantamentos**.

---

## 🔄 Mudança de Comportamento

### ❌ **Antes**
- O tipo (Valor Fixo ou Percentual) era determinado **automaticamente** pelo campo `impacto` do Provento/Desconto selecionado
- Usuário não tinha controle direto sobre qual campo usar
- Dependia da configuração prévia do Provento/Desconto

### ✅ **Depois**
- Campo **"Tipo de Valor"** separado e independente
- Usuário escolhe explicitamente: **"Valor Fixo"** ou **"Percentual do Salário"**
- Mais flexibilidade e clareza na interface
- Padrão consistente com o formulário de Adiantamentos

---

## 🛠️ Implementação Técnica

### 1. **Formulário** (`funcionarios/forms.py`)

Adicionamos um campo `ChoiceField` para seleção do tipo:

```python
class LancamentoFixoForm(forms.ModelForm):
    TIPO_VALOR_CHOICES = [
        ('F', 'Valor Fixo'),
        ('P', 'Percentual do Salário'),
    ]
    
    tipo_valor = forms.ChoiceField(
        choices=TIPO_VALOR_CHOICES,
        initial='F',
        label='Tipo de Valor',
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ...
        
        # Define valor inicial baseado no registro existente
        if self.instance.pk:
            if self.instance.valor:
                self.fields['tipo_valor'].initial = 'F'
            elif self.instance.percentual:
                self.fields['tipo_valor'].initial = 'P'
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_valor = cleaned_data.get('tipo_valor')
        valor = cleaned_data.get('valor')
        percentual = cleaned_data.get('percentual')
        
        # Validar que o campo correto foi preenchido
        if tipo_valor == 'F' and not valor:
            self.add_error('valor', 'Informe o valor fixo')
        
        if tipo_valor == 'P' and not percentual:
            self.add_error('percentual', 'Informe o percentual')
        
        return cleaned_data
```

**Mudanças:**
- ✅ Novo campo `tipo_valor` com choices 'F' e 'P'
- ✅ Inicialização automática ao editar registros existentes
- ✅ Validação customizada para garantir preenchimento correto

---

### 2. **Template** (`templates/funcionarios/lancamento_fixo_form.html`)

Template atualizado com Alpine.js para reatividade:

```html
<div x-data="{ tipoValor: '{{ form.tipo_valor.value|default:'F' }}' }">
    <form method="post">
        <!-- Provento/Desconto -->
        <select name="provento_desconto" required>
            <option value="">---------</option>
            {% for pd in proventos_descontos %}
                <option value="{{ pd.pk }}">{{ pd }}</option>
            {% endfor %}
        </select>
        
        <!-- NOVO: Campo Tipo de Valor -->
        <select name="tipo_valor" x-model="tipoValor" required>
            <option value="F">Valor Fixo</option>
            <option value="P">Percentual do Salário</option>
        </select>
        
        <!-- Valor Fixo (aparece se tipoValor === 'F') -->
        <div x-show="tipoValor === 'F'">
            <input type="number" name="valor" placeholder="0.00" />
        </div>
        
        <!-- Percentual (aparece se tipoValor === 'P') -->
        <div x-show="tipoValor === 'P'">
            <input type="number" name="percentual" placeholder="0.00" />
        </div>
    </form>
</div>
```

**Características:**
- ✅ Alpine.js com `x-model` para binding bidirecional
- ✅ `x-show` para alternar campos dinamicamente
- ✅ Inicialização correta ao carregar e ao editar

---

### 3. **Views** (`funcionarios/views.py`)

Views atualizam para limpar o campo não utilizado:

```python
@login_required
def lancamento_fixo_create(request, funcionario_pk):
    if request.method == 'POST':
        form = LancamentoFixoForm(request.POST)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.funcionario = funcionario
            
            # Limpar campo não utilizado
            tipo_valor = form.cleaned_data.get('tipo_valor')
            if tipo_valor == 'F':
                lancamento.percentual = None
            elif tipo_valor == 'P':
                lancamento.valor = None
            
            lancamento.save()
```

**Lógica:**
- ✅ Se tipo = 'F' (Valor Fixo) → limpa `percentual`
- ✅ Se tipo = 'P' (Percentual) → limpa `valor`
- ✅ Garante que apenas um campo fica preenchido no banco

---

### 4. **Modelo** (`funcionarios/models.py`)

Validação do modelo atualizada para ser mais flexível:

```python
class LancamentoFixo(TimeStampedModel):
    def clean(self):
        """Validações do lançamento"""
        if self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError('Data de fim não pode ser anterior à data de início')
        
        # Valida que foi preenchido valor OU percentual
        if not self.valor and not self.percentual:
            raise ValidationError('Informe o valor fixo ou o percentual')
        
        if self.valor and self.percentual:
            raise ValidationError('Informe apenas valor fixo OU percentual, não ambos')
```

**Mudança:**
- ❌ **Removida** validação baseada em `provento_desconto.impacto`
- ✅ **Nova** validação: deve ter **valor OU percentual**, mas não ambos

---

## 🎯 Fluxo de Uso

### Criar Novo Lançamento

1. Selecione o **Provento/Desconto**
2. Escolha o **Tipo de Valor**:
   - "Valor Fixo" → Campo R$ aparece
   - "Percentual do Salário" → Campo % aparece
3. Preencha o campo exibido
4. Defina as datas e observações
5. Salve

### Editar Lançamento Existente

1. O formulário carrega com o **Tipo de Valor** já selecionado
2. O campo correspondente (Valor ou Percentual) aparece preenchido
3. É possível alterar o tipo e preencher o outro campo
4. Ao salvar, o campo anterior é limpo automaticamente

---

## 🎨 Resultado Visual

```
┌────────────────────────────────────────┐
│ Provento/Desconto *                    │
│ ┌────────────────────────────────────┐ │
│ │ Vale Transporte                  ▼ │ │
│ └────────────────────────────────────┘ │
│                                        │
│ Tipo de Valor *                        │
│ ┌────────────────────────────────────┐ │
│ │ Valor Fixo                       ▼ │ │  ← NOVO CAMPO
│ └────────────────────────────────────┘ │
│                                        │
│ Valor Fixo (R$) *                      │
│ ┌────────────────────────────────────┐ │
│ │ 0.00                               │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

---

## ✅ Vantagens

1. **UX Consistente**: Mesmo padrão do formulário de Adiantamentos
2. **Mais Claro**: Usuário escolhe explicitamente o tipo
3. **Flexível**: Não depende da configuração do Provento/Desconto
4. **Validado**: Garante que apenas o campo correto é preenchido
5. **Reativo**: Alteração instantânea sem reload da página

---

## 🧪 Como Testar

### Teste 1: Criar com Valor Fixo
1. Acesse: `/funcionarios/1/lancamentos-fixos/novo/`
2. Selecione um Provento/Desconto
3. Mantenha "Valor Fixo" selecionado
4. Preencha o campo R$
5. Salve → Deve criar corretamente

### Teste 2: Criar com Percentual
1. Acesse: `/funcionarios/1/lancamentos-fixos/novo/`
2. Selecione um Provento/Desconto
3. Mude para "Percentual do Salário"
4. Preencha o campo %
5. Salve → Deve criar corretamente

### Teste 3: Editar e Trocar Tipo
1. Edite um lançamento existente com Valor Fixo
2. Mude para "Percentual do Salário"
3. Preencha o novo campo %
4. Salve → Valor fixo deve ser limpo, percentual deve ser salvo

### Teste 4: Validação
1. Escolha "Valor Fixo" mas não preencha o campo
2. Tente salvar → Deve exibir erro
3. Preencha o campo
4. Salve → Deve funcionar

---

## 📂 Arquivos Modificados

- ✅ `funcionarios/forms.py` (linhas 53-112)
- ✅ `funcionarios/views.py` (linhas 166-238)
- ✅ `funcionarios/models.py` (linhas 260-270)
- ✅ `templates/funcionarios/lancamento_fixo_form.html` (linhas 20-79)

---

## 🚀 Status

**✅ IMPLEMENTADO COM SUCESSO**

O formulário de Lançamentos Fixos agora segue o padrão de UX do Adiantamentos, com campo explícito para escolha do tipo de valor.
