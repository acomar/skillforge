# Taxonomia e nomes

Uma skill tem **uma categoria principal** no YAML de `SKILL.md`, dentro de `metadata.category`.

| Categoria | Aplicação |
| --- | --- |
| `architecture` | DDD, EventStorming, arquitetura, Team Topologies |
| `engineering` | Código, testes, DevOps, engenharia reversa, legados |
| `leadership` | Gestão, estratégia, indicadores, desenvolvimento de equipes |
| `automation` | Fluxos, bots, integrações, agentes e produtividade |
| `content` | Vídeo, storytelling, roteiros, edição e criação |
| `marketing` | Distribuição, redes sociais, SEO, afiliados |
| `product` | Produto digital, UX, discovery, experimentos |
| `data` | Extração, análise, transformação e visualização |
| `operations` | Governança, auditorias, processos e gestão de skills |
| `research` | Pesquisa, investigação, curadoria de conhecimento |

Exemplo de metadados:

```yaml
---
name: eventstorming-facilitator
description: Facilita entrevistas e transforma material de processos em modelos EventStorming. Use ao mapear eventos, comandos, atores e políticas de um domínio.
metadata:
  category: architecture
  status: experimental
  version: "0.1.0"
---
```

## Convenção para nomes

- Prefira o resultado da capacidade, como `eventstorming-facilitator`, `video-storytelling`, `mainframe-test-design`.
- Use somente letras minúsculas, números e hífens.
- Evite nomes genéricos como `helper`, `expert` ou `new-skill`.
- Não use nomes de clientes, marcas pessoais ou siglas internas desnecessárias.
- `name` no YAML deve ser igual ao nome da pasta.
