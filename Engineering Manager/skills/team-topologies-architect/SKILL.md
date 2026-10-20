---
name: team-topologies-architect
description: "Diagnostica ownership, limites de times e dependencias segundo Team Topologies. Use quando há squads com ownership sobreposto, dependências cruzadas, repasses constantes, sustentação centralizada, alta carga cognitiva ou debate sobre reorganização."
metadata:
  category: architecture
  status: experimental
  version: "1.0.0"
---

# Team Topologies Architect

## Quando ativar
Quando há squads com ownership sobreposto, dependências cruzadas, repasses constantes, sustentação centralizada, alta carga cognitiva ou debate sobre reorganização.

## Resultado que esta super skill produz
Desenhar fronteiras de equipe e interações para maximizar fluxo de valor e autonomia responsável.

## Entradas mínimas
- Contexto: time/serviço ou fluxo, objetivo, gargalo percebido, riscos e restrições de governança.
- Fontes: relato com data e confiança, documentos/indicadores quando disponíveis e responsáveis pelas decisões.
- Se faltar dado, marque como `não informado`; não invente baseline, capacidade ou aprovação.

## Protocolo de execução
1. Mapeie fluxos de valor reais, produtos/serviços, aplicações e todas as mudanças realizadas por cada equipe.
2. Registre ownership atual: quem modifica, testa, aprova, implanta, opera, investiga e corrige.
3. Classifique as interações atuais e a carga cognitiva de cada time; evite decidir tipo de time apenas pelo organograma.
4. Considere os quatro tipos de Team Topologies: stream-aligned, enabling, complicated subsystem e platform, justificando a escolha.
5. Projete os três modos explícitos de interação: collaboration com duração definida, X-as-a-Service com interface clara, facilitating com objetivo de habilitação.
6. Defina limites de decisão e responsabilidade pela produção compatíveis com segurança, segregação e regras de change.
7. Experimente em um fluxo piloto com janela de 30–60 dias; meça filas, espera, dependência e incidentes antes de expandir.

## Perguntas de investigação, use conforme necessidade
- Qual fluxo de valor cada squad consegue levar do problema à produção?
- Duas squads podem modificar o mesmo componente? Quem responde pelo resultado?
- O que exige coordenação porque a arquitetura ou governança ainda não permite autonomia?

## Artefatos de saída obrigatórios quando aplicáveis
- Mapa As-Is de times e fluxos
- Matriz de ownership por serviço e etapa
- Topologia-alvo com interações definidas
- Piloto de reorganização incremental

## Indicadores de sucesso
- Número de handoffs por demanda
- Tempo de espera entre equipes
- % de mudanças concluídas sem dependência bloqueante
- Carga cognitiva percebida

## Contramétricas / salvaguardas
- Incidentes, risco regulatório e burnout não podem aumentar com a redução de handoffs.

## Antipadrões a detectar
- Reorganizar por estética do organograma
- Criar platform team sem produto interno nem clientes
- Impor “full cycle” ignorando limites regulatórios
- Ter vários donos sem accountable definido

## Integrações com outras super skills
- flow-bottleneck-optimizer
- reliability-modernization

## Referências e rastreabilidade
- Skelton e Pais, Team Topologies, quatro tipos e três modos de interação.
- Grove, caps. 7–10 (formas organizacionais e controle).
- Sinek, caps. 5–6 (coerência e confiança).

## Estrutura da resposta desta skill
1. **Problema e objetivo** em até três frases.
2. **Fatos confirmados**, **hipóteses** e **dados ausentes** em blocos distintos.
3. **Causas prováveis** ordenadas por evidência/impacto.
4. **Até três intervenções**: ação, dono proposto, data de revisão sugerida e evidência de conclusão.
5. **Métricas e contramétricas**, riscos, exigências de governança e decisão humana necessária.
6. **Autonomia transferida**: qual responsabilidade passa do gerente para o time, em quais limites.
