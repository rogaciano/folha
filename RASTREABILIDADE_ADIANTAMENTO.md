# Rastreabilidade de Adiantamentos

## Implementação (14/12/2024)

Conforme estudo de arquitetura de folha de pagamento, foi implementada a **rastreabilidade completa** 
entre o **fato gerador** (adiantamento salarial) e o **fato compensador** (desconto na folha mensal).

---

## Arquitetura Implementada

### Modelo Adiantamento (funcionarios/models.py)
```python
class Adiantamento(TimeStampedModel):
    STATUS_CHOICES = [
        ('P', 'Pendente'),      # Aguardando desconto
        ('D', 'Descontado'),    # Já foi compensado na folha
        ('C', 'Cancelado'),     # Cancelado manualmente
    ]
    
    funcionario = ForeignKey(Funcionario)
    data_adiantamento = DateField()
    valor = DecimalField(max_digits=10, decimal_places=2)
    status = CharField(choices=STATUS_CHOICES, default='P')
```

### Modelo ItemFolha (folha/models.py)
```python
class ItemFolha(TimeStampedModel):
    # ... outros campos ...
    
    # NOVO: Link direto para rastreabilidade
    adiantamento_origem = models.ForeignKey(
        Adiantamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Adiantamento Origem',
        related_name='itens_desconto',
        help_text='Referência ao adiantamento original (quando aplicável)'
    )
```

---

## Fluxo de Funcionamento

### 1. Lançamento do Adiantamento (Dia 15/20)
O adiantamento é registrado na tabela `Adiantamento` com:
- `status = 'P'` (Pendente)
- `data_adiantamento` = data do pagamento
- `valor` = valor pago

### 2. Geração da Folha Mensal (Dia 30/05)
Ao processar a folha mensal, o sistema automaticamente:

1. Busca adiantamentos pendentes do funcionário
2. Cria um `ItemFolha` com:
   - `provento_desconto` = Desconto de Adiantamento
   - `valor_lancado` = valor do adiantamento
   - `adiantamento_origem` = **link direto** ao registro original
3. Marca o adiantamento como `status = 'D'` (Descontado)

---

## Rastreabilidade

### No Django Admin
- Lista de `ItemFolha` exibe coluna **"Adiant. Origem"**
- Clicando no link, navega diretamente para o registro original do adiantamento
- Mostra ícone 📋 com a data do adiantamento

### Via Código
```python
# Do ItemFolha para o Adiantamento
item = ItemFolha.objects.get(pk=123)
if item.adiantamento_origem:
    print(f"Origem: {item.adiantamento_origem.data_adiantamento}")
    print(f"Valor original: R$ {item.adiantamento_origem.valor}")

# Do Adiantamento para os itens de desconto
adiantamento = Adiantamento.objects.get(pk=456)
descontos = adiantamento.itens_desconto.all()
for item in descontos:
    print(f"Descontado em: {item.evento_pagamento.folha_pagamento.periodo_referencia}")
```

---

## Tratamento Tributário

O desconto do adiantamento é **apenas financeiro**:
- Não reduz a base de cálculo de INSS
- Não reduz a base de cálculo de IRRF
- Afeta apenas o valor líquido a receber

Isso está correto conforme a legislação trabalhista brasileira, onde o adiantamento 
é um pagamento antecipado do salário, não uma dedução da base tributável.

---

## Migration Aplicada

```
folha/migrations/0003_adiciona_rastreabilidade_adiantamento.py
    - Add field adiantamento_origem to itemfolha
```

---

## Próximos Passos (Opcionais)

1. **Relatório de Adiantamentos**: Criar view/relatório mostrando todos os adiantamentos 
   e seus respectivos descontos vinculados.

2. **Validação de Consistência**: Implementar check que verifica se todo adiantamento 
   com status 'D' possui um ItemFolha correspondente.

3. **Desfazer Desconto**: Permitir reverter o desconto de um adiantamento 
   (voltar status para 'P' e excluir o ItemFolha).
