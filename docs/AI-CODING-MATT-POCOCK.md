# Matt Pocock: Workflow for AI Coding

**Fonte:** [Workshop completo](https://www.youtube.com/watch?v=-QFHIoCo-Ko), *AI Engineer Europe 2026*, aproximadamente 96 minutos.

**Transcrição pública consultada:** https://mwolf.dev/library/full-walkthrough-workflow-for-ai-coding-matt-pocock/full-walkthrough-workflow-for-ai-coding-matt-pocock

**Repositórios oficiais:** [Skills](https://github.com/mattpocock/skills) e [Sandcastle](https://github.com/mattpocock/sandcastle).

> Este documento é uma **análise original em português, organizada por marcações de tempo**, não uma reprodução nem tradução literal da transcrição do vídeo. A transcrição pública é de terceiros e pode ter imprecisões. Consulte o vídeo original para conferir passagens.

## Guia de conteúdo com pontos do vídeo

| Tempo aproximado | Tema | Aplicação prática |
| --- | --- | --- |
| 00:00–05:00 | Fundamentos de engenharia continuam úteis com IA; limite prático de qualidade em contexto longo | Não colocar o projeto inteiro no prompt |
| 05:00–11:00 | Iteração em vez de plano rígido; Ralph; Memento e sessões novas | Manter backlog + renovar contexto por tarefa |
| 11:00–17:00 | O problema do desalinhamento; *grill-me* | Entrevistar antes de implementar |
| 17:00–29:00 | Demonstração de perguntas com respostas recomendadas; decisões humanas | Uma pergunta por turno; decisões difíceis ficam HITL |
| 29:00–39:00 | PRD como documento de destino, user stories, decisões e mapa de módulos | Criar `prd.md` sem confundi-lo com implementação |
| 39:00–47:00 | Divisão em fatias verticais; tickets e dependências | Produzir DAG de tickets com feedback integrado |
| 47:00–53:00 | Preparação do backlog e revisão humana | Aprovar as fatias antes do loop |
| 53:00–60:00 | Loop AFK simples; prompts, tickets e commits recentes | Executar uma tarefa por vez, inicialmente |
| 60:00–70:00 | Limites de autonomia, QA, feedback e padrões | Não delegar julgamento do produto |
| 70:00–77:00 | Importância de testes escritos antes da implementação e de feedback frequente | TDD red-green-refactor |
| 77:00–84:00 | Módulos profundos, contratos pequenos, manter visão da arquitetura | Projetar interfaces; delegar detalhes internos |
| 84:00–89:00 | Review, orientação de padrões e requisitos | Revisão independente do diff |
| 89:00–96:00 | Sandcastle: planejamento, sandboxes, worktrees, implementador, revisor e integração | Paralelizar apenas tarefas independentes em ambiente isolado |

**Nota:** A distribuição acima é uma indexação temática aproximada, não um índice oficial de capítulos.

## Princípios que a implementação preserva

1. **Alinhamento antes do artefato.** O ganho da entrevista é a compreensão compartilhada. O PRD registra o que foi decidido.
2. **Destino separado de jornada.** PRD descreve o resultado, tickets descrevem incrementos.
3. **Fatia vertical:** a primeira entrega deve atravessar as camadas mínimas necessárias, com feedback observável.
4. **HITL vs AFK:** julgamento de escopo, qualidade, segurança e produto pertence a humanos; implementação isolada pode ser automatizada.
5. **Feedback é o limite de velocidade.** Tipos, testes, execução real e revisão evitam que um erro seja replicado em escala.
6. **Contexto enxuto:** documento de handoff verificável, sessões novas e recuperação seletiva de informações.
7. **Deep modules:** interface simples com lógica interna coesa, contratos e testes externos.
8. **Revisão real:** implementar não prova que algo está certo; verificação e QA são fases distintas.
9. **Paralelismo controlado:** cada agente executa uma tarefa pronta, em ambiente isolado, respeitando dependências e conflitos.

## Ferramentas citadas e correspondência

| No workshop (2026) | Repositório atual e/ou adaptação SkillForge |
| --- | --- |
| `grill-me` | `ai-requirements-grilling`; upstream `grill-me` e `grill-with-docs` |
| `write-a-prd` | `ai-feature-spec`; upstream evoluiu para `to-spec` |
| `prd-to-issues` | `ai-vertical-slice-planning`; upstream `to-tickets` |
| `tdd` | `ai-tdd-execution`; upstream `tdd` |
| `improve-codebase-architecture` | `ai-deep-module-design`; upstream mantém skill de arquitetura |
| Review / QA | `ai-independent-review`; upstream `code-review` |
| Context reset / Memento | `ai-context-handoff`; upstream `handoff` |
| Ralph / Sandcastle | `ai-coding-orchestrator`; automação efetiva depende de executor autorizado |

Os nomes das skills originais podem evoluir depois do workshop. Para usar a edição original, consulte o README atual de `mattpocock/skills`.

## O que não é consenso científico ou garantia

- A ideia de que existe um corte fixo universal de desempenho em uma contagem específica de tokens é uma heurística do palestrante, não um limite válido para todos os modelos.
- Reset de contexto pode reduzir acúmulo de ruído, mas exige preservar decisões e evidências.
- TDD e revisão automatizada reduzem risco, mas não garantem ausência de bugs.
- Sandcastle não executa tarefas neste repositório apenas por citar seu nome; precisa de runtime, permissões, isolamento e instalação separados.

## Questões antes de uma execução real

- Qual repositório de aplicação será alterado?
- Qual runtime de agente será usado (Codex, Claude Code, outro)?
- Qual tracker (GitHub Issues, Jira, Markdown)?
- Que comandos realmente validam código, integração e deploy?
- Quais operações precisam de aprovação?
