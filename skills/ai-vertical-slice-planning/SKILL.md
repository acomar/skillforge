---
name: ai-vertical-slice-planning
description: Transforma um PRD em tickets pequenos de ponta a ponta com dependências explícitas e classificação HITL ou AFK. Use quando uma implementação precisa ser distribuída entre sessões ou agentes.
metadata:
  category: engineering
  status: experimental
  version: "0.1.0"
---

# AI Vertical Slice Planning

## Princípio
Cada ticket deve produzir um incremento vertical observável, atravessando as camadas necessárias. Evitar planos horizontais como 'criar todas as tabelas', 'criar todas as APIs', 'criar toda a UI' sem feedback integrado.

## Processo
1. Extrair histórias `US-xx`, interfaces e testes do PRD.
2. Construir a menor fatia executável que atravessa dados, lógica e apresentação **quando aplicável**. Exigir evidência de comportamento visível ou verificação automatizada.
3. Dividir por valor verificável, não por camada. Estimar tamanho pela capacidade de concluir/testar em uma sessão focada; quebrar tickets grandes.
4. Para cada ticket, incluir:
   - `id`, `title`, `type: AFK|HITL`, `blocked_by: []`, `user_stories: []`.
   - `scope`, `out_of_scope`, `modules`, `acceptance_tests`, `done_when`, `risks`.
5. Validar dependências como DAG, sem ciclos nem IDs órfãos.
6. Marcar como `HITL` decisões de produto, acesso a produção, QA subjetivo, aprovações e mudanças irreversíveis.
7. Identificar a fronteira pronta para execução: tickets AFK cujos bloqueadores estejam DONE.
8. Pedir revisão humana dos tickets e da ordem antes de iniciar execução.

## Exemplo de arquivo
```yaml
id: TASK-002
title: Exibir progresso ao concluir uma lição
type: AFK
blocked_by: [TASK-001]
user_stories: [US-01]
modules: [ProgressService, LessonView]
acceptance_tests:
  - "Após concluir uma lição, o painel mostra o progresso atualizado"
done_when:
  - "Teste falha antes da implementação e passa depois"
  - "Suite e lint executados"
```

## Saídas
`issues/TASK-xxx.md` por ticket + `issues/INDEX.md` com grafo e ordem sugerida.

## Falhas bloqueantes
Ticket sem teste, ciclo de dependência, entrega horizontal desconectada, inferência de aprovação ou concorrência em arquivos compartilhados não coordenada.
