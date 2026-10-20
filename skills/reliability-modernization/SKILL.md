---
name: reliability-modernization
description: "Planeja confiabilidade, sustentacao e modernizacao de legados. Use quando modernizar COBOL/mainframe/JCL/batches para Java, reduzir MIPS, redefinir sustentação, melhorar observabilidade ou migração gradual de serviços críticos."
metadata:
  category: engineering
  status: experimental
  version: "1.0.0"
---

# Reliability & Modernization

## Quando ativar
Quando modernizar COBOL/mainframe/JCL/batches para Java, reduzir MIPS, redefinir sustentação, melhorar observabilidade ou migração gradual de serviços críticos.

## Resultado que esta super skill produz
Evoluir sistemas críticos com segurança, evidência de equivalência, rollback e ownership explícito.

## Entradas mínimas
- Contexto: time/serviço ou fluxo, objetivo, gargalo percebido, riscos e restrições de governança.
- Fontes: relato com data e confiança, documentos/indicadores quando disponíveis e responsáveis pelas decisões.
- Se faltar dado, marque como `não informado`; não invente baseline, capacidade ou aprovação.

## Protocolo de execução
1. Inventarie serviços, programas, jobs, dados, dependências, janelas batch, SLAs, riscos de negócio e donos.
2. Construa mapa As-Is com ordem JCL/job/programa, entradas/saídas e efeitos colaterais; identifique conhecimento não documentado.
3. Defina objetivo de modernização e seus limites: custo/MIPS, resiliência, tempo de change, risco, independência e equivalência funcional.
4. Escolha uma fatia vertical pequena e reversível; explicite convivência e corte de tráfego ou de processamento.
5. Estabeleça golden datasets, reconciliação de saídas, contrato, testes de regressão, validação de volume/performance e observabilidade.
6. Desenhe cutover, rollback, critérios de go/no-go, aprovações, segregação de funções e testes de contingência.
7. Meça segurança e benefício real antes de desligar componentes antigos; mantenha mapa de ownership durante convivência.

## Perguntas de investigação, use conforme necessidade
- Qual job pode ser isolado sem quebrar a sequência noturna?
- Como provar equivalência de saldos, lançamentos, arquivos e totalizadores?
- Qual falha desencadearia rollback e quem o autorizaria?

## Artefatos de saída obrigatórios quando aplicáveis
- Mapa de dependências de batches
- Matriz de equivalência e evidências
- Plano de coexistência/cutover/rollback
- Roadmap por fatias de risco decrescente

## Indicadores de sucesso
- Divergência de saídas reconciliadas
- Incidentes por mudança
- Cumprimento de janela batch
- Custo/MIPS com premissas transparentes
- Tempo para recuperar serviço

## Contramétricas / salvaguardas
- Nenhuma economia justifica perda de integridade, violação regulatória ou indisponibilidade não aceitável.

## Antipadrões a detectar
- Big bang sem rollback
- Desligar legado antes de reconciliação real
- Assumir Java mais rápido/custo menor sem benchmark
- Ignorar operações/CAB e especialistas de negócio

## Integrações com outras super skills
- team-topologies-architect
- engineering-excellence

## Referências e rastreabilidade
- Grove, caps. 1–2 (fluxos e qualidade), cap. 3 (alavancagem).
- Team Topologies (ownership e subsistemas complexos).
- DORA (delivery e estabilidade).

## Estrutura da resposta desta skill
1. **Problema e objetivo** em até três frases.
2. **Fatos confirmados**, **hipóteses** e **dados ausentes** em blocos distintos.
3. **Causas prováveis** ordenadas por evidência/impacto.
4. **Até três intervenções**: ação, dono proposto, data de revisão sugerida e evidência de conclusão.
5. **Métricas e contramétricas**, riscos, exigências de governança e decisão humana necessária.
6. **Autonomia transferida**: qual responsabilidade passa do gerente para o time, em quais limites.
