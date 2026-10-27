---
name: ai-coding-orchestrator
description: Orquestra o ciclo completo de desenvolvimento com IA, da ideia à entrega validada. Use quando o usuário quer implementar uma feature, corrigir problemas complexos ou iniciar um projeto com planejamento, tickets, testes e revisão.
metadata:
  category: automation
  status: experimental
  version: "0.1.0"
---

# AI Coding Orchestrator

## Objetivo
Conduzir uma mudança de software com as decisões humanas nos pontos certos e implementação automatizável em tarefas pequenas. Inspirado no workshop *Workflow for AI Coding* de Matt Pocock. Esta skill compõe outras skills, mas não executa magicamente agentes externos.

## Entradas
- Objetivo do usuário e repositório ou código-fonte relevante.
- Restrições, contexto de negócio e definição inicial de sucesso.
- Ferramentas realmente disponíveis (testes, Git, gerenciador de tickets, sandbox).

## Etapas
1. **Descobrir contexto.** Ler instruções do repositório, scripts, testes, arquitetura e documentação relevante. Não carregar toda a base indiscriminadamente.
2. **Alinhar a solução.** Acionar `ai-requirements-grilling`; uma pergunta por vez, sempre com recomendação e trade-offs. Manter decisões em aberto visíveis.
3. **Pesquisar/prototipar quando houver incerteza real.** Registrar fontes e decisões; protótipos são descartáveis e não contam como feature entregue.
4. **Definir destino.** Acionar `ai-feature-spec` para gerar PRD, casos de uso, critérios de aceite, módulos previstos e fora de escopo.
5. **Definir jornada.** Acionar `ai-vertical-slice-planning` e revisar com humano o grafo de dependências antes de executar.
6. **Executar tickets prontos.** Em cada ticket `AFK`, iniciar contexto limpo, carregar apenas tarefa + contrato + padrões necessários e acionar `ai-tdd-execution`. Se não houver executor, fornecer comandos/tickets sem afirmar que executou.
7. **Revisão independente.** Acionar `ai-independent-review` em contexto separado; revisar fidelidade à especificação e padrões de engenharia.
8. **QA humana.** Apresentar prova de funcionamento, riscos e roteiro de validação. Nenhuma publicação, deploy ou merge irreversível sem autorização explícita.
9. **Aprendizado.** Registrar mudanças úteis de contexto, decisões e possíveis melhorias do ambiente. Não sobrescrever decisões antigas sem revisão.

## Estados e contratos
`IDEA -> ALIGNING -> SPEC_READY -> TICKETS_APPROVED -> IMPLEMENTING -> REVIEW -> HUMAN_QA -> DONE`.
Também há `BLOCKED`, `REWORK` e `CANCELLED`.
- Transitar para SPEC_READY somente com requisitos e dúvidas explícitas.
- Para TICKETS_APPROVED, dependências e tamanho dos tickets precisam ser revisados.
- Para DONE, critérios de aceite devem estar comprovados; em falta de execução, registrar PENDENTE.

## Regras de autonomia
- **HITL:** objetivos, escolhas de produto, mudanças de escopo, aprovação de tickets, QA, publicação e decisões de risco.
- **AFK autorizável:** pesquisa, exploração, implementação isolada, testes locais e revisão automatizada.
- Não executar ações destrutivas, acessar produção, usar credenciais, alterar permissões ou publicar sem autorização.
- Limitar concorrência a tickets sem dependências e sem arquivos conflitantes; usar branches/worktrees isolados quando disponíveis.
- Se a sessão ficar extensa, usar `ai-context-handoff` e reiniciar com o documento resumido, não carregar automaticamente o histórico inteiro.

## Saída por entrega
Relatório com `objetivo`, `decisões`, `escopo`, `tickets e dependências`, `evidências de testes`, `resultado da revisão`, `pendências` e `próximo passo`.

## Não usar
Para perguntas rápidas, pequenos ajustes sem risco ou atividades sem código; não impor PRD e Kanban a tarefas triviais.
