# SkillForge

Biblioteca versionada de **skills para agentes de IA**, criada para reutilizar conhecimento, processos e automações em diferentes ferramentas.

Cada skill é independente, portátil e segue o padrão [Agent Skills](https://agentskills.io/specification).

## Estrutura

```text
skillforge/
├── skills/                  # Skills prontas, uma pasta por habilidade
│   └── skillforge-maintainer/
│       ├── SKILL.md
│       └── references/
├── templates/               # Modelo para criar uma nova skill
├── scripts/                 # Gerador e validador
├── tests/                   # Testes da estrutura
├── docs/                    # Categorias, organização e instalação
├── .github/workflows/       # Validação automática no GitHub
├── AGENTS.md                # Orientações para agentes que editarem este repositório
└── CONTRIBUTING.md          # Como contribuir e manter a qualidade
```

**Importante:** as skills ficam diretamente em `skills/<nome-da-skill>/`. Não criamos `skills/engenharia/<skill>/`, porque vários agentes e instaladores esperam uma pasta própria por skill. As categorias são registradas em `metadata.category` no `SKILL.md`.

## Criar uma skill

```bash
python -m pip install -r requirements-dev.txt
python scripts/new_skill.py eventstorming-facilitator \
  --category architecture \
  --description "Facilita entrevistas e modelagem EventStorming a partir de processos e documentos."
python scripts/validate_skills.py
```

Depois, edite `skills/eventstorming-facilitator/SKILL.md` e inclua `references/`, `scripts/` e `assets/` apenas se forem realmente necessários. O comando acima **cria somente um esqueleto**, não uma skill finalizada.

## Skills disponíveis

- [skillforge-maintainer](skills/skillforge-maintainer/SKILL.md): criar, revisar e manter esta biblioteca de skills.
- [video-editing-longform-pt](skills/video-editing-longform-pt/SKILL.md): analisar referências e recriar ou editar vídeos longos, com capítulos, retomada e validação. Status experimental.
- [manga-hq-story-script-pt](skills/manga-hq-story-script-pt/SKILL.md): examinar páginas de HQ/mangá e criar narração original com evidências por painel, no padrão manga azul. Status experimental.
- [manga-hq-video-editor-pt](skills/manga-hq-video-editor-pt/SKILL.md): montar roteiro, áudio e imagens em vídeo com fundo azul, painéis ciano, zooms e fades sincronizados. Inclui builder e renderer local. Status experimental.

## Organização e uso

- [Arquitetura do repositório](docs/STRUCTURE.md)
- [Categorias e convenções de nomes](docs/CATEGORIES.md)
- [Instalação no Codex e Claude Code](docs/INSTALLATION.md)
- [Sugestões de próximas skills](docs/BACKLOG.md)
- [Guia para contribuições](CONTRIBUTING.md)

## Verificação

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_skills.py
python -m unittest discover -s tests -v
```

Toda alteração em `main` e todo pull request passam pela validação automática. Não coloque API keys, credenciais ou dados sensíveis nas skills.
