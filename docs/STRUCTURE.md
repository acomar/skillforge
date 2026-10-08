# Arquitetura do SkillForge

## Princípio central

**Uma skill = uma pasta = uma capacidade reutilizável.**

A hierarquia das skills é propositalmente rasa:

```text
skills/
  eventstorming-facilitator/
    SKILL.md
    references/       # somente se necessário
    scripts/          # somente se necessário
    assets/           # somente se necessário
  strategic-planning/
    SKILL.md
```

Os nomes acima são **exemplos de estrutura**, não skills já publicadas.

## Por que não organizar por pastas temáticas?

Padrões de descoberta de skills e instaladores podem esperar uma estrutura direta, como `skills/<skill>/SKILL.md` ou `.agents/skills/<skill>/SKILL.md`. Uma hierarquia `skills/<categoria>/<skill>` exige configuração extra e dificulta instalação por URL.

O SkillForge usa:
- Pasta: identificador técnico e único da skill.
- `metadata.category`: categoria temática, para organizar o catálogo.
- `metadata.status`: maturidade (`experimental`, `stable` ou `deprecated`).
- `metadata.version`: versão da skill.

## Estrutura interna

```text
minha-skill/
├── SKILL.md               # Obrigatório: metadados + instruções
├── references/            # Opcional: conhecimento aprofundado
├── scripts/               # Opcional: scripts executáveis
└── assets/                # Opcional: arquivos-modelo e recursos
```

**Evite pastas vazias e arquivos `.gitkeep` desnecessários.** Crie cada diretório no momento em que existir conteúdo.

## Responsabilidade das pastas do repositório

- `skills/`: skills utilizáveis por agentes.
- `templates/`: molde para novas skills.
- `scripts/`: ferramentas para manutenção do repositório.
- `tests/`: testes dessas ferramentas.
- `docs/`: regras, documentação e catálogo planejado.
- `.github/`: checks e colaboração.
- `AGENTS.md`: instruções para agentes de desenvolvimento que modificarem o SkillForge.

## Evite

- Duplicar a mesma skill em `.claude/skills/` e `.agents/skills/` dentro deste repositório. Instale as skills relevantes no destino quando precisar delas.
- Criar skills vazias só para reservar nomes.
- Colocar prompts de um caso individual como se fossem skills reutilizáveis.
- Armazenar chaves de API ou dados sensíveis em `assets/`.
