---
name: flow-bottleneck-optimizer
description: "Mapeia fluxos de valor e reduz gargalos, filas e handoffs. Use quando o lead time é alto, há filas de change, CAB, teste e implantação, multitarefa excessiva, WIP alto ou percepção de “time lento” sem dados."
metadata:
  category: operations
  status: experimental
  version: "1.0.0"
---

# Flow & Bottleneck Optimizer

## Quando ativar
Quando o lead time é alto, há filas de change, CAB, teste e implantação, multitarefa excessiva, WIP alto ou percepção de “time lento” sem dados.

## Resultado que esta super skill produz
Encontrar e elevar a restrição do sistema de entrega, do pedido à produção, sem transferir gargalos para outra etapa.

## Entradas mínimas
- Contexto: time/serviço ou fluxo, objetivo, gargalo percebido, riscos e restrições de governança.
- Fontes: relato com data e confiança, documentos/indicadores quando disponíveis e responsáveis pelas decisões.
- Se faltar dado, marque como `não informado`; não invente baseline, capacidade ou aprovação.

## Protocolo de execução
1. Defina início/fim do fluxo e diferencie lead time de demanda, lead time de mudança (DORA) e tempo ativo.
2. Capture uma amostra real de demandas com timestamps por estado, reentradas e exceções.
3. Desenhe o fluxo: descoberta → análise → codificação → teste → validação → change/CAB → implantação → observação.
4. Calcule tempo de processamento, espera, retrabalho, WIP e bloqueios; identifique o passo limitante.
5. Formule 2–3 hipóteses causais e proponha experimentos de baixo risco: reduzir lote, melhorar critérios, paralelizar validações permitidas ou automatizar checks.
6. Se a restrição for governança obrigatória, otimize preparação, evidências e cadência, nunca contorne aprovações.
7. Valide antes/depois usando throughput, espera, instabilidade e impacto de cliente.

## Perguntas de investigação, use conforme necessidade
- Dos 55 dias de lead time, quantos são trabalho e quantos são espera?
- Qual etapa acumula mais itens e por quê?
- Quando removemos uma fila, qual próxima restrição surge?

## Artefatos de saída obrigatórios quando aplicáveis
- Value Stream Map e distribuição de tempos
- Pareto de bloqueios
- Backlog de hipóteses de melhoria
- Experimento com baseline e contramétricas

## Indicadores de sucesso
- Lead time ponta a ponta
- Tempo de espera por etapa
- WIP
- Taxa de retrabalho
- Tempo bloqueado por dependências

## Contramétricas / salvaguardas
- Falhas, retrabalho e violação de controles após aceleração.

## Antipadrões a detectar
- Reduzir tempo só do desenvolvimento e declarar vitória
- Confundir ocupação 100% com fluxo ótimo
- Tratar aprovação regulatória como desperdício eliminável sem análise

## Integrações com outras super skills
- engineering-excellence
- high-output-manager

## Referências e rastreabilidade
- Grove, caps. 1–2 (produção, passo limitante e indicadores), cap. 6 (planejamento).
- DORA, métricas e capabilities de entrega.

## Estrutura da resposta desta skill
1. **Problema e objetivo** em até três frases.
2. **Fatos confirmados**, **hipóteses** e **dados ausentes** em blocos distintos.
3. **Causas prováveis** ordenadas por evidência/impacto.
4. **Até três intervenções**: ação, dono proposto, data de revisão sugerida e evidência de conclusão.
5. **Métricas e contramétricas**, riscos, exigências de governança e decisão humana necessária.
6. **Autonomia transferida**: qual responsabilidade passa do gerente para o time, em quais limites.
