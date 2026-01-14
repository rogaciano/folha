# Sistema de Eventos de Pagamento

## 📋 Visão Geral

O sistema de **Eventos de Pagamento** foi implementado para resolver a limitação de ter apenas um pagamento por competência (mês/ano). Agora é possível gerenciar múltiplos eventos de pagamento dentro de uma mesma competência, permitindo:

- ✅ **Adiantamento quinzenal** com lançamentos específicos
- ✅ **Pagamento final** do mês
- ✅ **13º salário** parcelado
- ✅ **Férias** e **Rescisões**
- ✅ **Rastreabilidade completa** de cada pagamento
- ✅ **Status independente** para cada evento

---

## 🏗️ Arquitetura

### Estrutura Hierárquica

```
FolhaPagamento (Competência: 01/2025)
│
├── EventoPagamento (Adiantamento Quinzenal - 15/01/2025)
│   ├── ItemFolha (Funcionário A - Salário proporcional)
│   ├── ItemFolha (Funcionário A - Vale transporte)
│   ├── ItemFolha (Funcionário B - Salário proporcional)
│   └── ...
│
├── EventoPagamento (Pagamento Final - 30/01/2025)
│   ├── ItemFolha (Funcionário A - Saldo do salário)
│   ├── ItemFolha (Funcionário A - Horas extras)
│   ├── ItemFolha (Funcionário A - Desconto adiantamento)
│   └── ...
│
└── EventoPagamento (13º Salário - 1ª Parcela - 30/01/2025)
    ├── ItemFolha (Funcionário A - 13º proporcional)
    └── ...
```

### Modelos

#### FolhaPagamento (Competência)
- Representa o **mês/ano** de referência
- Contém múltiplos eventos de pagamento
- Status: Rascunho, Fechada, Paga, Cancelada

#### EventoPagamento (Novo)
- Representa um **evento específico** de pagamento
- Tipos disponíveis:
  - `AD` - Adiantamento Quinzenal
  - `PF` - Pagamento Final
  - `13` - 13º Salário
  - `FE` - Férias
  - `RE` - Rescisão
  - `OU` - Outros
- Campos principais:
  - `data_evento`: Data prevista/realizada do pagamento
  - `data_pagamento`: Data efetiva do pagamento (quando pago)
  - `status`: Rascunho, Fechado, Pago, Cancelado
  - `valor_total`: Calculado automaticamente

#### ItemFolha
- Agora referencia tanto a **FolhaPagamento** quanto o **EventoPagamento**
- Mantém compatibilidade com código existente

---

## 🚀 Como Usar

### 1. Criar uma Folha de Pagamento (Competência)

```python
from folha.services import FolhaService

# Cria a folha para Janeiro/2025 com evento padrão
folha = FolhaService.gerar_folha(mes=1, ano=2025, criar_evento_padrao=True)

# Ou sem evento padrão (para criar manualmente depois)
folha = FolhaService.gerar_folha(mes=1, ano=2025, criar_evento_padrao=False)
```

### 2. Criar um Evento de Adiantamento Quinzenal

```python
from datetime import date
from folha.services import FolhaService

# Cria evento de adiantamento quinzenal
evento_adiantamento = FolhaService.criar_evento_pagamento(
    folha=folha,
    tipo_evento='AD',
    descricao='Adiantamento Quinzenal 15/01/2025',
    data_evento=date(2025, 1, 15),
    processar_funcionarios=False  # Não processa automaticamente
)
```

### 3. Adicionar Lançamentos ao Evento

```python
from core.models import ProventoDesconto
from funcionarios.models import Funcionario
from decimal import Decimal

# Busca funcionário e provento
funcionario = Funcionario.objects.get(cpf='123.456.789-00')
provento_salario = ProventoDesconto.objects.get(codigo_referencia='SALARIO')

# Adiciona 50% do salário como adiantamento
valor_adiantamento = funcionario.salario_base * Decimal('0.5')

FolhaService.adicionar_item_manual(
    evento=evento_adiantamento,
    funcionario=funcionario,
    provento_desconto=provento_salario,
    valor=valor_adiantamento,
    justificativa='Adiantamento quinzenal - 50% do salário'
)
```

### 4. Criar Evento de Pagamento Final

```python
# Cria evento de pagamento final (com todos os funcionários)
evento_final = FolhaService.criar_evento_pagamento(
    folha=folha,
    tipo_evento='PF',
    descricao='Pagamento Final 30/01/2025',
    data_evento=date(2025, 1, 30),
    processar_funcionarios=True  # Processa todos automaticamente
)

# O sistema já lança:
# - Salário base
# - Lançamentos fixos gerais
# - Lançamentos fixos do funcionário
# - Descontos de adiantamentos pendentes
```

### 5. Gerenciar Status dos Eventos

```python
# Fechar evento (não permite mais edições)
evento_adiantamento.fechar_evento()

# Marcar como pago
evento_adiantamento.marcar_como_pago(data_pagamento=date(2025, 1, 15))

# Reabrir para edição
evento_adiantamento.reabrir_evento()
```

---

## 📊 Consultas Úteis

### Listar todos os eventos de uma folha

```python
eventos = folha.get_eventos_pagamento()
for evento in eventos:
    print(f"{evento.descricao} - {evento.get_status_display()} - R$ {evento.valor_total}")
```

### Verificar total pago vs pendente

```python
total_pago = folha.get_total_eventos_pagos()
total_pendente = folha.get_total_eventos_pendentes()

print(f"Total Pago: R$ {total_pago}")
print(f"Total Pendente: R$ {total_pendente}")
```

### Buscar itens de um evento específico

```python
itens = evento_adiantamento.itens.all().select_related('funcionario', 'provento_desconto')

for item in itens:
    print(f"{item.funcionario.nome_completo} - {item.provento_desconto.nome} - R$ {item.valor_lancado}")
```

---

## 🎯 Casos de Uso Práticos

### Caso 1: Adiantamento Quinzenal + Pagamento Final

```python
from datetime import date
from decimal import Decimal

# 1. Cria a folha de Janeiro/2025
folha = FolhaService.gerar_folha(mes=1, ano=2025, criar_evento_padrao=False)

# 2. Cria evento de adiantamento (dia 15)
evento_adiantamento = FolhaService.criar_evento_pagamento(
    folha=folha,
    tipo_evento='AD',
    descricao='Adiantamento Quinzenal 15/01',
    data_evento=date(2025, 1, 15),
    processar_funcionarios=False
)

# 3. Lança 40% do salário para cada funcionário
for contrato in folha.contratos_ativos.all():
    funcionario = contrato.funcionario
    provento = ProventoDesconto.objects.get(codigo_referencia='SALARIO')
    
    valor = funcionario.salario_base * Decimal('0.4')
    
    FolhaService.adicionar_item_manual(
        evento=evento_adiantamento,
        funcionario=funcionario,
        provento_desconto=provento,
        valor=valor,
        justificativa='Adiantamento quinzenal - 40%'
    )

# 4. Fecha e marca como pago
evento_adiantamento.fechar_evento()
evento_adiantamento.marcar_como_pago(data_pagamento=date(2025, 1, 15))

# 5. Cria evento de pagamento final (dia 30)
evento_final = FolhaService.criar_evento_pagamento(
    folha=folha,
    tipo_evento='PF',
    descricao='Pagamento Final 30/01',
    data_evento=date(2025, 1, 30),
    processar_funcionarios=True  # Lança salário integral + descontos
)

# 6. Adiciona desconto do adiantamento manualmente (se necessário)
desconto_adiantamento = ProventoDesconto.objects.get(codigo_referencia='ADIANTAMENTO')

for contrato in folha.contratos_ativos.all():
    funcionario = contrato.funcionario
    
    # Busca o valor do adiantamento pago
    valor_adiantado = evento_adiantamento.itens.filter(
        funcionario=funcionario
    ).aggregate(total=Sum('valor_lancado'))['total'] or Decimal('0')
    
    if valor_adiantado > 0:
        FolhaService.adicionar_item_manual(
            evento=evento_final,
            funcionario=funcionario,
            provento_desconto=desconto_adiantamento,
            valor=valor_adiantado,
            justificativa=f'Desconto adiantamento de 15/01'
        )
```

### Caso 2: 13º Salário Parcelado

```python
# 1ª Parcela em Novembro
evento_13_primeira = FolhaService.criar_evento_pagamento(
    folha=folha_novembro,
    tipo_evento='13',
    descricao='13º Salário - 1ª Parcela',
    data_evento=date(2025, 11, 30),
    processar_funcionarios=False
)

# Lança 50% do salário para cada funcionário
for contrato in folha_novembro.contratos_ativos.all():
    funcionario = contrato.funcionario
    provento_13 = ProventoDesconto.objects.get(codigo_referencia='13_SALARIO')
    
    valor = funcionario.salario_base * Decimal('0.5')
    
    FolhaService.adicionar_item_manual(
        evento=evento_13_primeira,
        funcionario=funcionario,
        provento_desconto=provento_13,
        valor=valor,
        justificativa='13º Salário - 1ª Parcela (50%)'
    )

# 2ª Parcela em Dezembro
evento_13_segunda = FolhaService.criar_evento_pagamento(
    folha=folha_dezembro,
    tipo_evento='13',
    descricao='13º Salário - 2ª Parcela',
    data_evento=date(2025, 12, 20),
    processar_funcionarios=False
)

# Lança os 50% restantes com descontos
```

---

## 🔧 Admin Django

O Django Admin foi atualizado para suportar eventos:

### Visualização de Folha
- Lista todos os eventos da folha
- Permite criar novos eventos inline
- Mostra status e valor total de cada evento

### Visualização de Evento
- Lista todos os itens (lançamentos) do evento
- Permite adicionar/editar itens
- Calcula automaticamente o valor total
- Controla status (Rascunho → Fechado → Pago)

---

## 📝 Migração de Dados

A migration `0002_adiciona_eventos_pagamento.py` foi criada para:

1. ✅ Criar o modelo `EventoPagamento`
2. ✅ Adicionar campo `evento_pagamento` em `ItemFolha`
3. ✅ **Migrar dados existentes**: Cria um evento padrão "Pagamento Final" para cada folha existente
4. ✅ Associar todos os itens existentes aos eventos criados
5. ✅ Manter compatibilidade com código existente

**Importante**: Todos os dados existentes foram preservados e migrados automaticamente!

---

## 🎨 Benefícios da Solução

### ✅ Flexibilidade Total
- Crie quantos eventos quiser por competência
- Cada evento pode ter lançamentos específicos
- Controle independente de status

### ✅ Rastreabilidade
- Histórico completo de todos os pagamentos
- Data prevista vs data efetiva
- Justificativas por item

### ✅ Gestão Simplificada
- Acompanhe cada pagamento separadamente
- Marque eventos como pagos individualmente
- Relatórios por evento ou consolidados

### ✅ Compatibilidade
- Código existente continua funcionando
- Migração automática de dados
- Sem perda de informações

---

## 🔄 Fluxo Completo de Trabalho

```
1. Criar Folha (Competência)
   ↓
2. Criar Evento de Adiantamento
   ↓
3. Adicionar Lançamentos ao Adiantamento
   ↓
4. Fechar e Pagar Adiantamento
   ↓
5. Criar Evento de Pagamento Final
   ↓
6. Sistema lança automaticamente:
   - Salário base
   - Lançamentos fixos
   - Descontos (incluindo adiantamento)
   ↓
7. Adicionar lançamentos manuais (se necessário)
   ↓
8. Fechar e Pagar Evento Final
   ↓
9. Fechar Folha (Competência)
```

---

## 📚 Referências

- **Modelos**: `folha/models.py`
- **Serviços**: `folha/services.py`
- **Admin**: `folha/admin.py`
- **Migration**: `folha/migrations/0002_adiciona_eventos_pagamento.py`

---

## 💡 Dicas

1. **Sempre crie eventos antes de adicionar lançamentos**
2. **Use `processar_funcionarios=True` para lançamentos automáticos**
3. **Feche eventos antes de marcar como pago**
4. **Mantenha descrições claras e padronizadas**
5. **Use as datas corretas para cada evento**

---

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação dos modelos
2. Consulte os exemplos de uso acima
3. Teste em ambiente de desenvolvimento primeiro
