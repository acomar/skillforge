# Instalação de skills

O repositório central guarda as skills em `skills/<nome>/`. Cada ferramenta pode exigir um diretório de descoberta diferente.

## Codex

Skills pessoais podem ser copiadas para `~/.agents/skills/`:

```bash
mkdir -p ~/.agents/skills
cp -R skills/skillforge-maintainer ~/.agents/skills/
```

Também é possível instalar habilidades a partir de diretórios do GitHub quando o instalador da versão do Codex suportar essa opção. Para repositórios privados, autentique seu GitHub.

## Claude Code

Skills pessoais podem ser copiadas para `~/.claude/skills/`:

```bash
mkdir -p ~/.claude/skills
cp -R skills/skillforge-maintainer ~/.claude/skills/
```

Para escopo somente de projeto, utilize `.claude/skills/` no projeto de destino.

## Outros agentes

Consulte o mecanismo de descoberta da ferramenta. O conteúdo de cada `SKILL.md` segue o padrão aberto Agent Skills, mas **caminhos de instalação e recursos extras variam entre produtos**.

## Atualização

Ao modificar uma skill no SkillForge, atualize a cópia instalada no destino. A instalação por `cp` não cria sincronização automática.

## Segurança

Leia skills de terceiros antes de instalá-las. Scripts e instruções executados pelo agente devem ser tratados como código com acesso às permissões do ambiente.
