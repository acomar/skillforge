---
name: engineering-excellence
description: "Desenvolve capacidades de engenharia, entrega continua e qualidade. Use quando há necessidade de melhorar DORA, testes, CI/CD, qualidade, confiabilidade das mudanças, Developer Experience ou padrões técnicos."
metadata:
  category: engineering
  status: experimental
  version: "1.0.0"
---

# Engineering Excellence

## Quando ativar
Quando há necessidade de melhorar DORA, testes, CI/CD, qualidade, confiabilidade das mudanças, Developer Experience ou padrões técnicos.

## Resultado que esta super skill produz
Aumentar throughput e estabilidade simultaneamente, criando sistemas de entrega repetíveis e com feedback rápido.

## Entradas mínimas
- Contexto: time/serviço ou fluxo, objetivo, gargalo percebido, riscos e restrições de governança.
- Fontes: relato com data e confiança, documentos/indicadores quando disponíveis e responsáveis pelas decisões.
- Se faltar dado, marque como `não informado`; não invente baseline, capacidade ou aprovação.

## Protocolo de execução
1. Identifique serviço, criticidade e baseline; documente o que é medido de fato.
2. Meça as cinco métricas DORA atuais: change lead time, deployment frequency, failed deployment recovery time, change fail rate, deployment rework rate.
3. Complemente com testes, qualidade, experiência dev e impacto de produto; nunca rankeie pessoas por deploys.
4. Mapeie práticas habilitadoras: integração contínua, automação de testes, revisão de código, deploy seguro, observabilidade e arquitetura desacoplada.
5. Escolha uma restrição dominante e um experimento: automatizar smoke test, fixture, pipeline, análise estática, rollback ou detecção.
6. Defina critérios de qualidade por criticidade e guardrails de segurança/compliance.
7. Revise evolução em tendência, com contramétricas, e compartilhe conhecimento entre os times.

## Perguntas de investigação, use conforme necessidade
- O que faz uma alteração segura ser difícil hoje?
- Qual etapa é manual por exigência de controle e qual é manual por falta de automação?
- Qual indicador melhorará se o experimento funcionar, e qual pode piorar?

## Artefatos de saída obrigatórios quando aplicáveis
- Scorecard DORA por serviço
- Mapa de capacidades de engenharia
- Roadmap técnico priorizado
- Experimento de melhoria validável

## Indicadores de sucesso
- Cinco métricas DORA atuais
- Cobertura útil de testes críticos
- Tempo de feedback do pipeline
- Experiência do desenvolvedor agregada

## Contramétricas / salvaguardas
- Estabilidade operacional, retrabalho, sobrecarga, incidentes e valor de negócio.

## Antipadrões a detectar
- Usar deploys por pessoa como produtividade
- Otimizar frequência de deploy ignorando falhas
- Definir percentual de cobertura como único critério de teste
- Confundir tempo de recuperação de deploy com MTTR geral

## Integrações com outras super skills
- flow-bottleneck-optimizer
- reliability-modernization

## Referências e rastreabilidade
- DORA, cinco métricas https://dora.dev/guides/dora-metrics/.
- DORA capabilities https://dora.dev/capabilities/.
- Grove, cap. 2 (indicadores), cap. 3 (alavancagem).

## Estrutura da resposta desta skill
1. **Problema e objetivo** em até três frases.
2. **Fatos confirmados**, **hipóteses** e **dados ausentes** em blocos distintos.
3. **Causas prováveis** ordenadas por evidência/impacto.
4. **Até três intervenções**: ação, dono proposto, data de revisão sugerida e evidência de conclusão.
5. **Métricas e contramétricas**, riscos, exigências de governança e decisão humana necessária.
6. **Autonomia transferida**: qual responsabilidade passa do gerente para o time, em quais limites.
