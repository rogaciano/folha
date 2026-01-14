# Fluxo Operacional do Sistema de Folha de Pagamento

## Visão Geral do Ciclo Mensal

O ciclo de folha de pagamento segue uma sequência lógica de eventos que garantem
a correta apuração e pagamento dos funcionários.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CICLO MENSAL DE FOLHA                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   DIA 01-05          DIA 15-20           DIA 25-30          DIA 30-05      │
│   ┌───────┐         ┌───────────┐       ┌──────────┐       ┌──────────┐    │
│   │ PASSO │         │  PASSO    │       │  PASSO   │       │  PASSO   │    │
│   │   1   │ ──────► │    2      │ ────► │   3-4    │ ────► │   5-6    │    │
│   │ Abrir │         │Adiantam.  │       │Lançam.   │       │ Fechar   │    │
│   │Compet.│         │ Massivo   │       │Finais    │       │ e Pagar  │    │
│   └───────┘         └───────────┘       └──────────┘       └──────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PASSO 1: Abrir Competência (Início do Mês)

### Quando: Dia 01 a 05 do mês

### O que acontece:
- Cria-se a **Folha de Pagamento** para o mês/ano
- O sistema identifica todos os **contratos ativos**
- Opcionalmente, cria um evento padrão de "Pagamento Final"

### Via Django Admin:
1. Acesse **Folha → Folhas de Pagamento → Adicionar**
2. Preencha:
   - **Mês**: 12
   - **Ano**: 2024
   - **Status**: Rascunho
3. Salve

### Via Código (recomendado):
```python
from folha.services import FolhaService

# Cria a folha e já processa todos os funcionários
folha = FolhaService.gerar_folha(mes=12, ano=2024)
print(f"Folha criada: {folha.periodo_referencia}")
print(f"Funcionários: {folha.contratos_ativos.count()}")
```

### Resultado:
- Folha criada em status "Rascunho"
- Evento "Pagamento Final 12/2024" criado
- Itens lançados automaticamente:
  - ✅ Salário Base de cada funcionário
  - ✅ Lançamentos Fixos Gerais (ex: VR, VT)
  - ✅ Lançamentos Fixos Individuais
  - ✅ Adiantamentos pendentes (se houver)

---

## PASSO 2: Adiantamento Salarial Massivo (Meio do Mês)

### Quando: Dia 15 a 20 do mês

### O que acontece:
- Cria-se um **Evento de Adiantamento** dentro da competência
- Lança-se adiantamentos para todos (ou alguns) funcionários
- Os adiantamentos ficam com status "Pendente" até o fechamento

### Via Django Admin:
1. Acesse **Funcionários → Adiantamentos → Adicionar**
2. Para cada funcionário, preencha:
   - **Funcionário**: Selecione
   - **Data**: 15/12/2024
   - **Valor**: 1.200,00 (ou 40% do salário)
   - **Status**: Pendente
3. Repita para cada funcionário (trabalhoso!)

### Via Código - Lançamento Massivo (recomendado):
```python
from folha.services import FolhaService
from folha.models import FolhaPagamento
from datetime import date
from decimal import Decimal

# 1. Busca a folha da competência
folha = FolhaPagamento.objects.get(mes=12, ano=2024)

# 2. Cria evento de adiantamento massivo
# Opção A: Por percentual (40% do salário)
evento = FolhaService.criar_evento_adiantamento_massivo(
    folha=folha,
    descricao='Adiantamento Quinzenal 15/12',
    data_evento=date(2024, 12, 15),
    percentual=Decimal('40.00'),  # 40% do salário base
)

# Opção B: Por valor fixo
evento = FolhaService.criar_evento_adiantamento_massivo(
    folha=folha,
    descricao='Adiantamento Quinzenal 15/12',
    data_evento=date(2024, 12, 15),
    valor=Decimal('1000.00'),  # R$ 1.000 para todos
)

# Opção C: Filtrar por setor ou função
evento = FolhaService.criar_evento_adiantamento_massivo(
    folha=folha,
    descricao='Adiantamento - Setor Produção',
    data_evento=date(2024, 12, 15),
    percentual=Decimal('40.00'),
    filtros={'setor_id': 1}  # Apenas setor com ID 1
)

print(f"Evento criado: {evento}")
print(f"Valor total: R$ {evento.valor_total}")
```

### Resultado:
- Evento tipo "AD" (Adiantamento) criado na folha
- Registro de `Adiantamento` criado para cada funcionário
- Status do adiantamento: "Pendente"
- Funcionários receberão o valor no dia 15/20

---

## PASSO 3: Lançamentos Manuais (Final do Mês)

### Quando: Dia 25 a 30 do mês

### O que acontece:
- Adiciona-se itens que não são fixos
- Exemplos: Horas extras, Comissões, Faltas, Atrasos

### Via Django Admin:
1. Acesse **Folha → Eventos de Pagamento**
2. Clique no evento "Pagamento Final 12/2024"
3. Na seção de Itens, adicione:
   - **Funcionário**: João Silva
   - **Provento/Desconto**: Horas Extras
   - **Valor**: 350,00

### Via Código:
```python
from folha.services import FolhaService
from folha.models import FolhaPagamento, EventoPagamento
from funcionarios.models import Funcionario
from core.models import ProventoDesconto
from decimal import Decimal

# 1. Busca as referências
folha = FolhaPagamento.objects.get(mes=12, ano=2024)
evento = folha.eventos.get(tipo_evento='PF')  # Pagamento Final
funcionario = Funcionario.objects.get(cpf='123.456.789-00')
provento_he = ProventoDesconto.objects.get(codigo_referencia='HORAS_EXTRAS')

# 2. Adiciona item manual
item = FolhaService.adicionar_item_manual(
    evento=evento,
    funcionario=funcionario,
    provento_desconto=provento_he,
    valor=Decimal('350.00'),
    justificativa='20 horas extras em dezembro'
)

print(f"Item adicionado: {item}")
```

### Tipos de Lançamentos Comuns:

| Provento/Desconto | Tipo | Observação |
|-------------------|------|------------|
| Horas Extras | Provento | Calculado sobre hora normal |
| Comissão | Provento | Variável por funcionário |
| Falta | Desconto | Dia não trabalhado |
| Atraso | Desconto | Proporcional ao tempo |
| Empréstimo Consignado | Desconto | Parcela mensal fixa |
| Pensão Alimentícia | Desconto | Percentual ou valor fixo |

---

## PASSO 4: Revisar Lançamentos Fixos (Conferência)

### Quando: Antes de fechar a folha

### O que verificar:
Os lançamentos fixos são aplicados automaticamente ao gerar a folha. Verifique se estão corretos:

### Via Django Admin:
1. Acesse **Core → Lançamentos Fixos Gerais** (aplicados a todos)
2. Acesse **Funcionários → Lançamentos Fixos** (individuais)

### Lançamentos Fixos Gerais (exemplo):
| Provento/Desconto | Valor/% | Aplicação |
|-------------------|---------|-----------|
| Vale Refeição | R$ 660,00 | Todos os funcionários |
| Vale Transporte | 6% | Sobre salário base |

### Lançamentos Fixos Individuais (exemplo):
| Funcionário | Provento/Desconto | Valor |
|-------------|-------------------|-------|
| João Silva | Plano de Saúde | R$ 250,00 |
| Maria Santos | Gratificação | R$ 500,00 |

---

## PASSO 5: Fechar a Folha

### Quando: Último dia útil do mês ou dia 05 do mês seguinte

### Pré-requisitos:
- ✅ Todos os lançamentos foram revisados
- ✅ Adiantamentos pendentes foram processados
- ✅ Totais conferidos

### O que acontece ao fechar:
1. Status muda de "Rascunho" → "Fechada"
2. Data de fechamento é registrada
3. Não é mais possível editar valores
4. Folha fica pronta para pagamento

### Via Django Admin:
1. Acesse **Folha → Folhas de Pagamento**
2. Selecione a folha 12/2024
3. Altere o status para "Fechada"
4. Salve

### Via Código:
```python
from folha.models import FolhaPagamento

folha = FolhaPagamento.objects.get(mes=12, ano=2024)

# Tenta fechar a folha
try:
    folha.fechar_folha()
    print(f"Folha fechada em: {folha.data_fechamento}")
except Exception as e:
    print(f"Erro ao fechar: {e}")
```

### Relatório de Conferência:
```python
from folha.models import FolhaPagamento

folha = FolhaPagamento.objects.get(mes=12, ano=2024)

print(f"=== RESUMO DA FOLHA {folha.periodo_referencia} ===")
print(f"Total Proventos: R$ {folha.total_proventos:,.2f}")
print(f"Total Descontos: R$ {folha.total_descontos:,.2f}")
print(f"Total Líquido:   R$ {folha.total_liquido:,.2f}")
print(f"Funcionários:    {folha.contratos_ativos.count()}")

# Detalhamento por funcionário
for resumo in folha.resumos.all():
    print(f"\n{resumo.funcionario.nome_completo}")
    print(f"  Proventos: R$ {resumo.total_proventos:,.2f}")
    print(f"  Descontos: R$ {resumo.total_descontos:,.2f}")
    print(f"  Líquido:   R$ {resumo.valor_liquido:,.2f}")
```

---

## PASSO 6: Processar Pagamentos

### Quando: Data de pagamento (dia 05 do mês seguinte ou conforme contrato)

### O que acontece:
1. Cada evento pode ser pago separadamente
2. Ao pagar, status muda para "Pago"
3. Data de pagamento efetivo é registrada

### Via Código:
```python
from folha.models import FolhaPagamento, EventoPagamento
from datetime import date

folha = FolhaPagamento.objects.get(mes=12, ano=2024)

# Pagar cada evento
for evento in folha.eventos.filter(status='F'):  # Apenas fechados
    evento.marcar_como_pago(data_pagamento=date.today())
    print(f"Pago: {evento.descricao} - R$ {evento.valor_total}")

# Após todos eventos pagos, marcar folha como paga
if folha.eventos.exclude(status='P').count() == 0:
    folha.marcar_como_paga()
    print(f"Folha {folha.periodo_referencia} marcada como paga!")
```

### Integração Bancária (futuro):
```python
# Gerar arquivo de remessa bancária
# (funcionalidade a ser implementada)
def gerar_remessa_bancaria(folha):
    linhas = []
    for resumo in folha.resumos.all():
        func = resumo.funcionario
        linhas.append({
            'banco': func.banco,
            'agencia': func.agencia,
            'conta': func.conta,
            'cpf': func.cpf,
            'nome': func.nome_completo,
            'valor': resumo.valor_liquido,
            'pix': func.chave_pix,
        })
    return linhas
```

---

## Resumo do Fluxo Completo

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           FLUXO COMPLETO                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────────┐                                                       │
│  │  01-05 do mês   │  PASSO 1: Abrir Competência                          │
│  │                 │  • Criar FolhaPagamento(mes, ano)                    │
│  │   FolhaService  │  • Processar contratos ativos                        │
│  │   .gerar_folha()│  • Lançar salários e fixos automaticamente           │
│  └────────┬────────┘                                                       │
│           │                                                                │
│           ▼                                                                │
│  ┌─────────────────┐                                                       │
│  │  15-20 do mês   │  PASSO 2: Adiantamento Massivo                       │
│  │                 │  • Criar EventoPagamento tipo 'AD'                   │
│  │   FolhaService  │  • Lançar adiantamentos (% ou valor fixo)            │
│  │   .criar_evento │  • Status: Pendente → será descontado no fechamento  │
│  │   _adiantamento │                                                       │
│  │   _massivo()    │                                                       │
│  └────────┬────────┘                                                       │
│           │                                                                │
│           ▼                                                                │
│  ┌─────────────────┐                                                       │
│  │  25-28 do mês   │  PASSO 3: Lançamentos Manuais                        │
│  │                 │  • Horas extras, comissões, faltas                   │
│  │   FolhaService  │  • Adicionar itens no evento de Pagamento Final      │
│  │   .adicionar_   │                                                       │
│  │   item_manual() │                                                       │
│  └────────┬────────┘                                                       │
│           │                                                                │
│           ▼                                                                │
│  ┌─────────────────┐                                                       │
│  │  28-30 do mês   │  PASSO 4: Conferência                                │
│  │                 │  • Revisar lançamentos fixos                         │
│  │   Revisar no    │  • Verificar totais por funcionário                  │
│  │   Django Admin  │  • Conferir adiantamentos descontados                │
│  └────────┬────────┘                                                       │
│           │                                                                │
│           ▼                                                                │
│  ┌─────────────────┐                                                       │
│  │  30 do mês      │  PASSO 5: Fechar Folha                               │
│  │                 │  • Status: Rascunho → Fechada                        │
│  │  folha.fechar_  │  • Data de fechamento registrada                     │
│  │  folha()        │  • Bloqueio de edições                               │
│  └────────┬────────┘                                                       │
│           │                                                                │
│           ▼                                                                │
│  ┌─────────────────┐                                                       │
│  │  05 do mês +1   │  PASSO 6: Processar Pagamentos                       │
│  │                 │  • Marcar eventos como pagos                         │
│  │  evento.marcar_ │  • Registrar data de pagamento efetivo               │
│  │  como_pago()    │  • Gerar comprovantes/remessas bancárias             │
│  └─────────────────┘                                                       │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Comandos Rápidos (Cheat Sheet)

```python
from folha.services import FolhaService, AdiantamentoService
from folha.models import FolhaPagamento, EventoPagamento
from datetime import date
from decimal import Decimal

# ========== PASSO 1: ABRIR COMPETÊNCIA ==========
folha = FolhaService.gerar_folha(mes=12, ano=2024)

# ========== PASSO 2: ADIANTAMENTO MASSIVO ==========
evento_ad = FolhaService.criar_evento_adiantamento_massivo(
    folha=folha,
    descricao='Adiantamento 15/12',
    data_evento=date(2024, 12, 15),
    percentual=Decimal('40.00')
)

# ========== PASSO 3: LANÇAMENTO MANUAL ==========
from funcionarios.models import Funcionario
from core.models import ProventoDesconto

func = Funcionario.objects.get(cpf='123.456.789-00')
prov = ProventoDesconto.objects.get(codigo_referencia='HORAS_EXTRAS')
evento_pf = folha.eventos.get(tipo_evento='PF')

FolhaService.adicionar_item_manual(
    evento=evento_pf,
    funcionario=func,
    provento_desconto=prov,
    valor=Decimal('500.00'),
    justificativa='25 horas extras'
)

# ========== PASSO 5: FECHAR FOLHA ==========
folha.fechar_folha()

# ========== PASSO 6: PAGAR ==========
for evento in folha.eventos.filter(status='F'):
    evento.marcar_como_pago()
folha.marcar_como_paga()
```

---

## Glossário

| Termo | Definição |
|-------|-----------|
| **Competência** | Mês/ano de referência da folha |
| **Evento** | Tipo de pagamento dentro da competência (Adiantamento, Pagamento Final, 13º, etc.) |
| **Provento** | Valor a receber (salário, horas extras, comissões) |
| **Desconto** | Valor a deduzir (INSS, IR, adiantamentos, faltas) |
| **Lançamento Fixo** | Valor recorrente aplicado automaticamente (VR, VT) |
| **Lançamento Manual** | Valor lançado pontualmente (horas extras do mês) |
| **Base de Cálculo** | Valor usado para cálculo de percentuais |
