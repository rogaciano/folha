## Escopo Implementado
- Eventos de pagamento com UI e ações (criar, listar, fechar, reabrir, pagar).
- Adiantamento massivo por valor ou percentual.
- 13º salário com 1ª/2ª parcela (50% cada).
- Referências principais:
  - Serviços: folha/services.py:129 (adiantamento massivo), folha/services.py:199 (13º por parcela)
  - Views e rotas: folha/views.py:178, 218, 271; folha/urls.py
  - Templates: templates/folha/folha_detail.html; templates/folha/evento_adiantamento_form.html; templates/folha/evento_13_form.html

## Cenários de Teste Manual
1. Gerar folha do mês em "Rascunho" e conferir contratos ativos.
2. Criar evento de Adiantamento (dia 15, percentual 50%) e marcar como pago; validar total do evento.
3. Criar evento de 13º (1ª parcela) e validar itens por funcionário e total.
4. Adicionar item manual (bônus/desc.) e conferir resumos por funcionário.
5. Fechar e marcar paga a folha; exportar PDF/Excel.

## Validações Esperadas
- Eventos aparecem no detalhe da folha com total e status.
- Adiantamentos são registrados como pendentes (para descontar no PF).
- 13º parcela lança 50% do salário por funcionário.
- Resumos e totais da competência batem com itens.

## Ajuste Necessário Antes de Homologar
- Garanti criação dos adiantamentos, porém a dedução automática no Pagamento Final (PF) só ocorre quando os adiantamentos existem no momento da geração da folha. Se o adiantamento for criado depois, o PF atual não reprocessa automaticamente.
- Proposta: ao fechar o evento "Pagamento Final", reprocessar adiantamentos pendentes:
  - No fechamento do evento PF, chamar a lógica de lançar adiantamentos pendentes e atualizar totais.
  - Local de ajuste: folha/views.py (em evento_fechar) detecta tipo PF e invoca reprocessamento antes de fechar.

## Limitações Conhecidas (para próxima iteração)
- 13º simplificado (50%/50%) sem cálculo proporcional por meses trabalhados, médias de variáveis, INSS/IR.
- Filtros de adiantamento por funcionário específico podem ser adicionados.

## Critérios de Aceite
- Criar, fechar e marcar pago eventos funcionam; totals corretos.
- Ao fechar PF, adiantamentos pendentes são descontados e marcados como "Descontado".

## Solicitação
- Confirmar que posso aplicar o ajuste de reprocessamento no fechamento do PF para garantir a dedução automática dos adiantamentos criados após a geração da folha, e avançar com testes guiados no ambiente.