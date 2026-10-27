---
name: ai-context-handoff
description: Produz um handoff mínimo, verificável e persistente para reiniciar uma sessão de desenvolvimento com IA. Use ao trocar de agente, tarefa, fase ou quando o contexto acumulado prejudicar o foco.
metadata:
  category: operations
  status: experimental
  version: "0.1.0"
---

# AI Context Handoff

## Finalidade
Preferir sessões novas por tarefa e recuperar contexto por documentos estáveis e código real, em vez de depender de histórico longo ou resumos sucessivos com erros acumulados.

## Procedimento
1. Identificar o objetivo da próxima sessão e apenas o que ela precisa saber.
2. Separar: **fatos verificados**, **decisões humanas**, **hipóteses**, **bloqueios** e **artefatos**.
3. Referenciar caminho exato de PRD/ticket/glossário/ADR, commit ou diff de base, e comandos de teste.
4. Registrar o último estado da tarefa, próximo passo executável e critério para determinar sucesso.
5. Remover informações redundantes, credenciais, dados pessoais e detalhes desconectados do próximo passo.
6. Em nova sessão, reler os arquivos citados e verificar se ainda correspondem ao código atual. Não pressupor que o handoff esteja correto ou atualizado.

## Contrato `HANDOFF.md`
```markdown
# Objetivo imediato
# Repositório / branch / commit base
# Tarefa e estado
# Decisões confirmadas
# Arquivos de referência (caminhos)
# Evidências e comandos de validação
# Bloqueios, hipóteses e riscos
# Próxima ação verificável
```

## Critérios
A próxima sessão deve conseguir retomar sem pedir dados já registrados; fatos não verificados permanecem rotulados. Não alegar que houve limpeza de contexto em ferramenta sem controle sobre isso.

## Não usar
Como substituto de documentação arquitetural permanente ou como permissão para apagar decisões importantes.
