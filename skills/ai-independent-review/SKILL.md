---
name: ai-independent-review
description: Revisa implementações de agentes em contexto independente sob os eixos de especificação e padrões de código. Use após implementação, antes de merge ou QA humana.
metadata:
  category: engineering
  status: experimental
  version: "0.1.0"
---

# AI Independent Review

## Objetivo
Revisão técnica independente com contexto curto. Não reutilizar justificativas não comprovadas do implementador como evidência.

## Entradas
Diff contra base fixa, ticket aprovado, PRD relevante, instruções do repositório, testes e resultados reais. Se não houver diff, registrar limitação e pedir os arquivos.

## Dois eixos independentes
**A. Fidelidade à especificação:** cada critério de aceite está coberto? Há regressão funcional, casos de borda, autorização, mudança além do escopo?

**B. Qualidade e padrões:** legibilidade, interfaces profundas, acoplamento, tratamento de erros, concorrência, segurança, performance, observabilidade, manutenção e testes. Carregar padrões de código explicitamente na revisão.

## Procedimento
1. Criar sessão nova, sem histórico extenso do implementador.
2. Ler contrato do ticket e diff; se possível, fazer as duas avaliações em contextos separados e consolidar achados.
3. Classificar achados `BLOCKER`, `MAJOR`, `MINOR`, `NIT`, cada um com arquivo/linha, evidência, consequência e sugestão.
4. Diferenciar falha comprovada de suspeita. Nunca inventar linhas ou resultados de execução.
5. Propor teste de regressão para cada falha de comportamento.
6. Se bloqueante, devolver `REWORK`; se não, emitir `REVIEWED` com riscos residuais e checklist de QA humana.

## Saída
`review.md` com: base do diff, resumo, tabela de achados, cobertura dos critérios, evidências, decisões, pendências e roteiro de QA.

## Limites
Revisão automatizada não substitui aprovação humana em mudanças sensíveis ou percepção visual de produto; não mergear automaticamente.
