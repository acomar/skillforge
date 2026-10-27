---
name: ai-tdd-execution
description: Implementa um ticket pequeno e testável seguindo red-green-refactor e feedback real. Use quando um ticket AFK foi aprovado e existem código, ambiente de execução e critérios de aceite.
metadata:
  category: engineering
  status: experimental
  version: "0.1.0"
---

# AI TDD Execution

## Pré-condições
Ticket `AFK` aprovado, dependências atendidas, repositório acessível, comandos de teste conhecidos e limite de permissões explícito.

## Procedimento
1. Iniciar contexto focado na tarefa. Ler ticket, PRD somente nas seções relacionadas, padrões de código e interface dos módulos necessários.
2. Inspecionar comportamento existente e identificar menor fronteira testável. Preservar compatibilidade e convenções locais.
3. Escrever teste capaz de falhar **pelo motivo correto**, ligado a critério de aceite. Executar e registrar evidência **RED**.
4. Fazer mudança mínima para satisfazer o comportamento. Executar o teste e registrar evidência **GREEN**.
5. Refatorar em passos pequenos, preservando a suíte. Evitar mockar a lógica que se quer provar.
6. Executar checks disponíveis e relevantes: tipos, lint, unitários, integração e build, conforme o projeto.
7. Inspecionar diff, verificar ausência de segredos e mudanças de escopo, e descrever evidências.
8. Atualizar ticket com resultado (`DONE`, `BLOCKED` ou `REWORK`), provas e riscos. Encaminhar para `ai-independent-review`.

## Saída de execução
```yaml
ticket: TASK-001
status: DONE|BLOCKED|REWORK
files_changed: []
red_evidence: ""
green_evidence: ""
checks: [{name: "", status: "PASS|FAIL|NOT_RUN", evidence: ""}]
tradeoffs: []
unverified: []
```

## Regras
- Não afirmar RED/GREEN quando não executou os testes.
- Se faltar ferramenta/ambiente, preparar implementação e marcar `NOT_RUN`; não marcar DONE sem evidência.
- Não modificar tickets não relacionados, não reescrever testes só para passar e não remover validações para silenciar falhas.
- Não fazer merge ou deploy sem autorização. Tarefas com risco não aprovado voltam para HITL.
