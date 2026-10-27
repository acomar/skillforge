# Exemplo: feature de pontos por conclusão de lição

Exemplo hipotético inspirado no tipo de feature demonstrado no workshop. Não corresponde a código real e não comprova execução.

## Entrevista

**Usuário:** Quero premiar alunos que concluem lições.

**Agente:** Os pontos devem ser retroativos para lições já concluídas? **Minha recomendação:** não na primeira versão, porque isso cria uma migração e regras de reconciliação. Alternativa: migração explícita com validação separada.

**Usuário:** Não nesta versão.

**Decisão registrada:** pontos apenas para conclusões futuras; comportamento retroativo fora do escopo.

## PRD resumido

- US-01: Ao completar uma lição nova, o aluno recebe 10 pontos uma única vez.
- US-02: O painel mostra pontuação total após a conclusão.
- AC-01: Duplicar a solicitação de conclusão não concede pontos extras.
- AC-02: Um evento existente antes do lançamento não altera a pontuação.
- Fora de escopo: histórico retroativo e ranking de usuários.
- Modulo proposto: `PointsService` com `awardForLessonCompletion(studentId, lessonId)`.

## Backlog

| Ticket | Tipo | Bloqueado por | Fatia |
| --- | --- | --- | --- |
| TASK-001 | AFK | nenhum | Concluir lição nova grava pontos e emite resultado consultável |
| TASK-002 | AFK | TASK-001 | Exibir total atualizado no painel |
| TASK-003 | HITL | TASK-002 | Validar experiência, risco e aceitação final |

## Implementação de TASK-001

1. RED: teste prova que 2 chamadas iguais rendem 10, não 20 pontos.
2. GREEN: serviço evita duplicidade com chave única ou transação adequada.
3. REFACTOR: extrair contrato mínimo e garantir regressão.
4. Revisão independente confere idempotência, concorrência, regra de negócio e testes.
5. QA humana verifica comportamento com aplicação real.

**Status deste exemplo:** apenas documentação, nenhum teste executado.
