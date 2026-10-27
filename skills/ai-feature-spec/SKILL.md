---
name: ai-feature-spec
description: Converte entendimento compartilhado em PRD verificável, decisões de implementação, mapa de módulos e critérios de aceite. Use depois da entrevista ou quando já houver requisitos claros.
metadata:
  category: product
  status: experimental
  version: "0.1.0"
---

# AI Feature Spec

## Entradas
`shared-understanding.md`, código real, fontes verificadas, glossário e decisões de arquitetura.

## Procedimento
1. Verificar afirmações técnicas contra o repositório; não inventar módulos, rotas ou schemas.
2. Descrever problema, público, resultado observável e histórias de usuário numeradas (`US-01`).
3. Definir exemplos e critérios de aceite testáveis por história, incluindo casos negativos e permissões.
4. Listar módulos existentes a alterar e módulos novos sugeridos, indicando interfaces e fronteiras.
5. Registrar decisões de implementação, impactos em dados, compatibilidade e migração.
6. Indicar estratégia de teste e feedback: tipos, unitários, integração, contrato, UI e regressão, conforme o sistema.
7. Registrar explicitamente `Fora de escopo`, alternativas recusadas, riscos e perguntas ainda abertas.
8. Não polir o PRD indefinidamente: ele expressa o **destino**; tickets expressam o **caminho**.

## Modelo mínimo de `prd.md`
```markdown
# [Feature]
## Problema e objetivo
## Usuários e histórias
### US-01 ...
Critérios de aceite: ...
## Fluxo esperado e exceções
## Módulos e contratos envolvidos
## Decisões técnicas e estratégia de testes
## Segurança, operação e migração
## Fora de escopo e decisões rejeitadas
## Riscos, premissas e perguntas abertas
## Definição de pronto
```

## Validação
- Cada história mapeia a pelo menos um critério de aceite.
- Cada decisão crítica tem fonte, justificativa ou marcação de hipótese.
- Todo item fora do escopo é inequívoco.
- O módulo sugerido não precisa existir, mas deve ser identificado como proposta.
- Quando faltarem informações bloqueantes, devolver ao entrevistador.
