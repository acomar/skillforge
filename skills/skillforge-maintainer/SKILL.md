---
name: skillforge-maintainer
description: Cria, revisa, organiza e evolui skills do repositório SkillForge seguindo o padrão Agent Skills. Use ao adicionar uma capacidade reutilizável, auditar uma skill existente, definir metadados ou preparar uma migração para o catálogo.
metadata:
  category: operations
  status: stable
  version: "1.0.0"
---

# SkillForge Maintainer

## Quando usar

Ative esta skill para criar, converter, organizar, documentar ou revisar skills que serão reutilizadas por agentes de IA.

## Quando não usar

Não acione para responder diretamente a um assunto de domínio, como programação, marketing ou EventStorming, se o usuário não pediu uma **skill** reutilizável.

## Processo

1. **Defina a capacidade.** Identifique o usuário-alvo, o evento que aciona a skill e a saída esperada. Evite escopo excessivamente amplo.
2. **Pesquise duplicidade.** Verifique se já existe uma pasta equivalente em `skills/`; prefira evoluir a existente.
3. **Classifique.** Escolha uma única categoria entre as definidas em `docs/CATEGORIES.md`.
4. **Crie a pasta.** No diretório raiz do SkillForge, rode `python scripts/new_skill.py <slug> --category <categoria> --description "<descrição>"`.
5. **Escreva o `SKILL.md`.** Substitua as instruções genéricas por um procedimento real, critérios de uso, entradas, saídas, validações e exceções.
6. **Isole os detalhes.** Acrescente `references/` para documentação grande, `scripts/` para automação e `assets/` para modelos, apenas quando necessários.
7. **Revise a qualidade.** Leia [o checklist](references/QUALITY-CHECKLIST.md), valide riscos, dados sensíveis, dependências e portabilidade.
8. **Teste.** Experimente um caso normal, um ambíguo e um de falha; não afirme sucesso sem evidências.
9. **Valide.** Execute `python scripts/validate_skills.py` e `python -m unittest discover -s tests -v`.
10. **Publique com maturidade honesta.** Deixe como `experimental` enquanto houver instruções não testadas; use `stable` quando o comportamento estiver demonstrado.

## Critérios de aceitação

- Nome da pasta corresponde a `name`, em kebab-case.
- `description` inclui função e gatilho.
- Instruções podem ser seguidas por outro agente sem contexto oculto.
- Saída e verificação são observáveis.
- Não há segredos, credenciais ou dependências implícitas.

## Limites

- Não invente dados, funcionalidades implementadas ou resultados de testes.
- Não publique rascunhos como skills finalizadas.
- Nunca altere outras skills sem necessidade.
- Respeite permissões para operações em repositórios e sistemas externos.
