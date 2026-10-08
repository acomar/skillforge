# Instruções para agentes que trabalham no SkillForge

Este repositório é uma biblioteca de skills reutilizáveis, não um aplicativo.

1. Antes de criar ou editar skills, leia `docs/STRUCTURE.md`, `docs/CATEGORIES.md` e o padrão [Agent Skills](https://agentskills.io/specification).
2. Cada skill deve morar em `skills/<nome-em-kebab-case>/SKILL.md`. Não agrupe as skills em subpastas de categorias.
3. `SKILL.md` precisa começar com YAML frontmatter contendo `name`, `description` e `metadata.category`, `metadata.status` e `metadata.version`.
4. A descrição deve dizer **o que a skill faz** e **quando deve ser acionada**. Documente também quando não deve ser usada, se houver sobreposição.
5. Escreva processos executáveis, entradas, saídas, validações e limites. Nunca invente requisitos, resultados de testes ou fontes.
6. Use `references/` para detalhes consultados sob demanda, `scripts/` para automações e `assets/` para modelos. Evite arquivos decorativos.
7. Mantenha instruções pequenas e autoexplicativas. Prefira caminhos relativos ao diretório da skill para seus recursos.
8. Nunca inclua tokens, senhas, credenciais, dados internos sensíveis ou links privados de acesso.
9. Para criar uma skill, use `scripts/new_skill.py` e depois substitua todos os campos a completar pelo conteúdo real.
10. Antes de concluir, execute `python scripts/validate_skills.py` e `python -m unittest discover -s tests -v`.
11. Não altere skills fora do escopo do pedido. Não declare uma skill como estável se ainda for apenas um rascunho.
