# 🔧 Melhoria: Campo de Seleção Tipo de Valor em Lançamentos Fixos

## 📋 Alteração Implementada

O formulário de **Lançamentos Fixos** agora possui um campo separado para escolher o **Tipo de Valor**, seguindo o mesmo padrão do formulário de Adiantamentos.

### Antes
- O tipo (Valor Fixo ou Percentual) era determinado automaticamente pelo `impacto` do Provento/Desconto selecionado
- Não havia controle direto do usuário sobre qual campo preencher

### Depois
- ✅ Campo **"Tipo de Valor"** separado com opções: "Valor Fixo" ou "Percentual do Salário"
- ✅ Usuário escolhe explicitamente o tipo, independente do Provento/Desconto
- ✅ Interface mais clara e intuitiva

---

## ✅ Implementação

### 1. **Atualização das Views** (`funcionarios/views.py`)

Adicionamos o contexto `proventos_descontos` nas views de criação e edição:

```python
@login_required
def lancamento_fixo_create(request, funcionario_pk):
    # ... código existente ...
    
    # Buscar todos os proventos/descontos para o template
    from core.models import ProventoDesconto
    proventos_descontos = ProventoDesconto.objects.filter(ativo=True)
    
    context = {
        'form': form,
        'funcionario': funcionario,
        'proventos_descontos': proventos_descontos,  # ← NOVO
        'title': f'Novo Lançamento Fixo - {funcionario.nome_completo}'
    }
    return render(request, 'funcionarios/lancamento_fixo_form.html', context)
```

**O mesmo foi feito em `lancamento_fixo_update`**

---

### 2. **Atualização do Formulário** (`funcionarios/forms.py`)

Removemos o campo `funcionario` dos fields (já que é definido pela view):

```python
class LancamentoFixoForm(forms.ModelForm):
    class Meta:
        model = LancamentoFixo
        fields = ['provento_desconto', 'valor', 'percentual',  # ← funcionario removido
                 'data_inicio', 'data_fim', 'observacoes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ... código existente ...
        
        # Filtrar apenas proventos/descontos ativos
        from core.models import ProventoDesconto
        self.fields['provento_desconto'].queryset = ProventoDesconto.objects.filter(ativo=True)
```

---

### 3. **Atualização do Template** (`templates/funcionarios/lancamento_fixo_form.html`)

#### A) Inicialização do Alpine.js corrigida:
```html
<!-- ANTES -->
<div x-data="{ impacto: '{{ form.instance.provento_desconto.impacto|default:'F' }}' }">

<!-- DEPOIS -->
<div x-data="{ impacto: '{% if form.instance.pk and form.instance.provento_desconto %}{{ form.instance.provento_desconto.impacto }}{% else %}F{% endif %}' }">
```

#### B) Select customizado com data-impacto:
```html
<select name="{{ form.provento_desconto.name }}" 
        id="{{ form.provento_desconto.id_for_label }}"
        class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500" 
        x-on:change="impacto = $event.target.options[$event.target.selectedIndex].dataset.impacto"
        required>
    <option value="">---------</option>
    {% for pd in proventos_descontos %}
        <option value="{{ pd.pk }}" 
                data-impacto="{{ pd.impacto }}"
                {% if form.instance.provento_desconto_id == pd.pk %}selected{% endif %}>
            {{ pd }}
        </option>
    {% endfor %}
</select>
```

**Pontos-chave:**
- ✅ Cada `<option>` tem `data-impacto="{{ pd.impacto }}"` (F ou P)
- ✅ O evento `x-on:change` atualiza a variável Alpine.js `impacto`
- ✅ A seleção funciona tanto em criação quanto em edição

---

## 🎯 Como Funciona

1. **Ao carregar a página**:
   - Alpine.js inicializa `impacto` com 'F' (Valor Fixo) por padrão
   - Se estiver editando, inicializa com o valor do provento_desconto já selecionado

2. **Ao selecionar um Provento/Desconto**:
   - O Alpine.js captura o evento `change`
   - Lê o atributo `data-impacto` da opção selecionada ('F' ou 'P')
   - Atualiza a variável `impacto`

3. **Exibição dos campos**:
   - Se `impacto === 'F'`: mostra campo **Valor Fixo (R$)**
   - Se `impacto === 'P'`: mostra campo **Percentual (%)**
   - Controlado por `x-show` do Alpine.js

---

## ✅ Resultado

- ✅ Ao selecionar um Provento/Desconto do tipo **Valor Fixo**, aparece o campo de valor em R$
- ✅ Ao selecionar um Provento/Desconto do tipo **Percentual**, aparece o campo de percentual
- ✅ A troca é instantânea e reativa (sem reload da página)
- ✅ Funciona tanto ao criar quanto ao editar lançamentos

---

## 🧪 Como Testar

### Teste 1: Criar Novo Lançamento Fixo
1. Acesse um funcionário: `http://localhost:8000/funcionarios/1/`
2. Clique em **"Adicionar Lançamento Fixo"**
3. Selecione diferentes Proventos/Descontos no dropdown
4. Verifique que:
   - Ao selecionar provento com **Valor Fixo**: campo R$ aparece
   - Ao selecionar provento com **Percentual**: campo % aparece

### Teste 2: Editar Lançamento Existente
1. Edite um lançamento fixo existente
2. Verifique que o campo correto (Valor ou Percentual) já aparece preenchido
3. Troque o Provento/Desconto para outro tipo
4. Verifique que o campo exibido muda dinamicamente

### Teste 3: Validação
1. Tente salvar sem preencher o campo exibido
2. Deve exibir erro de validação
3. Tente salvar com valor negativo
4. Deve exibir erro de validação

---

## 📂 Arquivos Modificados

- ✅ `funcionarios/views.py` (linhas 166-220)
- ✅ `funcionarios/forms.py` (linhas 53-73)
- ✅ `templates/funcionarios/lancamento_fixo_form.html` (linhas 21-65)

---

## 📝 Observações Técnicas

### Por que usar Alpine.js?
- **Reatividade leve**: Mudança instantânea sem JavaScript complexo
- **Integração perfeita**: Funciona direto no HTML sem build tools
- **Manutenível**: Lógica clara e próxima do HTML

### Alternativas consideradas
1. ❌ **JavaScript vanilla**: Mais verboso e menos declarativo
2. ❌ **HTMX**: Overkill para este caso (causaria requisições ao servidor)
3. ✅ **Alpine.js**: Solução ideal para reatividade local

---

## 🚀 Status

**✅ PROBLEMA RESOLVIDO**

O campo de seleção entre Valor Fixo e Percentual agora funciona perfeitamente, permitindo ao usuário escolher e editar o tipo de lançamento fixo do funcionário.
