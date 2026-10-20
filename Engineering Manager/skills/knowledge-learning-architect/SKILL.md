---
name: knowledge-learning-architect
description: "Reduz conhecimento concentrado e desenvolve aprendizagem coletiva. Use quando uma aplicação depende de uma ou duas pessoas, o onboarding é lento, há documentação inexistente, perda de contexto, rotatividade ou pouca capacidade de diagnóstico."
metadata:
  category: leadership
  status: experimental
  version: "1.0.0"
---

# Knowledge & Learning Architect

## Quando ativar
Quando uma aplicação depende de uma ou duas pessoas, o onboarding é lento, há documentação inexistente, perda de contexto, rotatividade ou pouca capacidade de diagnóstico.

## Resultado que esta super skill produz
Transformar conhecimento tácito em competência distribuída e rastreável, reduzindo bus factor sem burocracia documental.

## Entradas mínimas
- Contexto: time/serviço ou fluxo, objetivo, gargalo percebido, riscos e restrições de governança.
- Fontes: relato com data e confiança, documentos/indicadores quando disponíveis e responsáveis pelas decisões.
- Se faltar dado, marque como `não informado`; não invente baseline, capacidade ou aprovação.

## Protocolo de execução
1. Mapeie componentes críticos, quem domina, frequência de incidentes/mudanças e impacto da indisponibilidade.
2. Classifique risco de concentração e lacunas de autonomia operacional/técnica, sem expor dados individuais desnecessários.
3. Priorize uma jornada real de negócio ou batch e crie mapa de regras, dependências e evidência de fonte.
4. Institua pairing, shadowing, treinamento prático e revisão cruzada vinculados ao trabalho cotidiano.
5. Crie documentação viva mínima: propósito, interfaces, regras, jobs, observabilidade, testes, runbook e como validar uma mudança.
6. Valide aprendizado fazendo outra pessoa explicar, modificar ou diagnosticar o fluxo em ambiente permitido.
7. Adote rotina leve de atualização após incidente, mudança e onboarding, com ownership explícito.

## Perguntas de investigação, use conforme necessidade
- Se o especialista estiver ausente, que mudanças param?
- Qual documento permitiria a outra pessoa executar um diagnóstico seguro hoje?
- Como testar aprendizado sem transformar documentação em métrica de vaidade?

## Artefatos de saída obrigatórios quando aplicáveis
- Mapa de competências por componente
- Plano de pares e sucessores
- Runbooks/documentação vivos
- Exercícios de capacidade comprovada

## Indicadores de sucesso
- % de componentes críticos com cobertura de conhecimento demonstrada
- Tempo de onboarding até tarefa segura
- Tempo de diagnóstico com runbook
- Mudanças independentes após capacitação

## Contramétricas / salvaguardas
- Não retirar capacidade produtiva indiscriminadamente, proteger tempo de formação e segurança.

## Antipadrões a detectar
- Documentar tudo sem uso nem revisão
- Declarar backup apenas porque leu um documento
- Depender da IA como única fonte de regra de negócio
- Penalizar especialistas por compartilhar conhecimento

## Integrações com outras super skills
- leadership-coaching-master
- reliability-modernization

## Referências e rastreabilidade
- Grove, cap. 3 (treinamento como alavanca), cap. 12 (maturidade específica da tarefa).
- Sinek, cap. 6 (confiança).
- Team Topologies, colaboração e facilitação.

## Estrutura da resposta desta skill
1. **Problema e objetivo** em até três frases.
2. **Fatos confirmados**, **hipóteses** e **dados ausentes** em blocos distintos.
3. **Causas prováveis** ordenadas por evidência/impacto.
4. **Até três intervenções**: ação, dono proposto, data de revisão sugerida e evidência de conclusão.
5. **Métricas e contramétricas**, riscos, exigências de governança e decisão humana necessária.
6. **Autonomia transferida**: qual responsabilidade passa do gerente para o time, em quais limites.
