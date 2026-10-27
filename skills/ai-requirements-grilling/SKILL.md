---
name: ai-requirements-grilling
description: Entrevista o usuário com perguntas sequenciais e recomendações até estabelecer entendimento compartilhado de uma mudança de produto ou software. Use antes de definir solução com requisitos ambíguos.
metadata:
  category: product
  status: experimental
  version: "0.1.0"
---

# AI Requirements Grilling

## Objetivo
Eliminar desalinhamento antes da implementação. A entrevista é interação humana, nunca uma suposição automática.

## Entradas
Ideia, usuário-alvo, problema, código/documentos disponíveis, restrições, resultados e exemplos conhecidos.

## Procedimento
1. Reformular o objetivo em até três frases. Listar fatos confirmados separados de hipóteses.
2. Fazer **uma única pergunta por turno**. A pergunta deve resolver uma escolha, não ser uma pesquisa genérica.
3. Junto da pergunta, fornecer **resposta recomendada**, motivo e alternativa relevante. Usuário pode aceitar, mudar ou adiar.
4. Priorizar perguntas por impacto: usuários e problema, fluxos e exceções, dados/regras, experiência, arquitetura, segurança, testes, operação, fora de escopo.
5. Atualizar um registro interno de decisões: `id | pergunta | decisão | justificativa | status | impacto`.
6. Para hipóteses externas, pesquisar evidências antes de tratá-las como verdade. Para dúvidas de domínio, consultar especialista/documentação.
7. Nunca preencher silêncio como aprovação. Se uma escolha bloquear arquitetura ou produto, manter `ABERTA`.
8. Encerrar quando as decisões críticas estiverem resolvidas, o usuário pedir para seguir, ou restarem apenas pendências explicitamente não bloqueantes.

## Saídas
- `shared-understanding.md`: problema, usuários, decisões, riscos e exemplos.
- `GLOSSARY.md` sugerido, com termos do domínio e definições curtas.
- `open-questions.md` com questões não resolvidas e responsável.
- ADR proposto para escolhas técnicas de consequência relevante.

## Critérios de aceite
- Requisitos relevantes foram discutidos, não inventados.
- Exceções, não objetivos e limitações estão documentados.
- Termos críticos têm definição compartilhada.
- O usuário aprovou as decisões irreversíveis antes de seguir.

## Não usar
Para forçar dezenas de perguntas quando o problema já está especificado. Evitar repetir perguntas respondidas e questionários gigantes.
