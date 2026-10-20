# Engineering Manager AI | Super Skills v1.0

**Missão:** ajudar um gerente de engenharia a construir times autônomos de alta performance que entregam valor com qualidade, confiança, aprendizado e conformidade.

**Status:** kit de especificação e skills reutilizáveis, pronto para experimentar em ambientes que leem arquivos `SKILL.md` e instruções `AGENTS.md`. Não é um agente conectado a sistemas nem um workflow implantado.

## Concepção

O agente integra cinco planos, sem confundi-los:

1. **PROPÓSITO**: por que o trabalho existe e para quem cria valor. Referência: Simon Sinek, *Comece pelo Porquê*.
2. **ALAVANCAGEM**: como decisões, capacitação e sistemas geram resultados por meio dos times. Referência: Andrew S. Grove, *High Output Management*.
3. **AUTONOMIA ORGANIZACIONAL**: como definir ownership, limites e interações. Referência: Team Topologies.
4. **EXCELÊNCIA DE ENGENHARIA**: como entregar com fluxo, segurança e confiabilidade. Referências: DORA, DevOps, SRE.
5. **DESENVOLVIMENTO HUMANO**: como desenvolver competência, confiança, feedback e aprendizagem. Referências: Grove, Sinek, re:Work.

## Estrutura

```text
engineering-manager-ai/
├── AGENTS.md
├── agents/engineering-manager/AGENT.md
├── config/routing.yaml
├── skills/
│   ├── purpose-strategy-architect/SKILL.md
│   ├── high-output-manager/SKILL.md
│   ├── leadership-coaching-master/SKILL.md
│   ├── team-topologies-architect/SKILL.md
│   ├── flow-bottleneck-optimizer/SKILL.md
│   ├── engineering-excellence/SKILL.md
│   ├── product-portfolio-strategist/SKILL.md
│   ├── reliability-modernization/SKILL.md
│   ├── knowledge-learning-architect/SKILL.md
│   └── organizational-transformation/SKILL.md
├── references/
├── templates/
└── evals/
```

## Como usar

- Disponibilize os arquivos ao agente e use `AGENTS.md` como instrução-raiz.
- Como ponto de partida, peça: `Faça um diagnóstico da autonomia das squads Acre e Cuiabá, considerando as restrições de mainframe e change/CAB, e proponha as três intervenções de maior alavancagem.`
- O agente deve **investigar antes de recomendar**, explicitar fatos/hipóteses/ausências e oferecer ações com responsáveis propostos, métricas e verificações.
- Ajuste `config/routing.yaml` se as funções e o contexto mudarem.
- O agente **não possui** acesso a dados operacionais privados até que ferramentas/conectores sejam habilitados. Nenhuma skill concede autorização para mudanças de produção ou decisões formais de RH.

## Referências

- Simon Sinek, *Comece pelo Porquê* (edição Sextante, 2018), EPUB fornecido pelo usuário: Círculo Dourado (cap. 3), clareza, disciplina e consistência (cap. 5), confiança (cap. 6), comunicação (cap. 10), perda de propósito (cap. 11), descoberta do porquê (cap. 13).
- Andrew S. Grove, *High Output Management*, EPUB fornecido pelo usuário: produção e restrições (caps. 1–2), alavancagem gerencial (cap. 3), reuniões (cap. 4), decisões (cap. 5), planejamento e MBO (cap. 6), organização (caps. 7–10), motivação (cap. 11), Task-Relevant Maturity (cap. 12), avaliação e feedback (cap. 13).
- Matthew Skelton e Manuel Pais, *Team Topologies* e https://teamtopologies.com/key-concepts.
- DORA: https://dora.dev/guides/dora-metrics/ e https://dora.dev/capabilities/.
- Google re:Work: https://rework.withgoogle.com/en/guides/understanding-team-effectiveness.

As duas obras são fontes de conceitos; este pacote é uma síntese própria e não redistribui textos integrais nem arquivos EPUB. É preciso validar interpretações e hipóteses no contexto real.

## Ordem de implementação sugerida

1. Ativar orquestrador + `team-topologies-architect` + `high-output-manager` + `leadership-coaching-master`.
2. Conectar métricas e fluxos reais; adicionar `flow-bottleneck-optimizer` + `engineering-excellence`.
3. Incorporar as demais skills e avaliações automatizadas.

**Versão:** 1.0.0 | **Idioma:** PT-BR | **Data:** 2026-10-20

## Integração com o SkillForge

Este diretório `Engineering Manager/` contém o projeto integrado do agente, documentação, configuração, avaliações e modelos. Para seguir a convenção do repositório, as dez super skills também estão publicadas individualmente em `../skills/<slug>/SKILL.md`, com o mesmo conteúdo.

**Estado:** experimental. A presença dos arquivos não significa que o agente esteja instalado ou conectado às ferramentas corporativas.

- [`purpose-strategy-architect`](../skills/purpose-strategy-architect/SKILL.md)
- [`high-output-manager`](../skills/high-output-manager/SKILL.md)
- [`leadership-coaching-master`](../skills/leadership-coaching-master/SKILL.md)
- [`team-topologies-architect`](../skills/team-topologies-architect/SKILL.md)
- [`flow-bottleneck-optimizer`](../skills/flow-bottleneck-optimizer/SKILL.md)
- [`engineering-excellence`](../skills/engineering-excellence/SKILL.md)
- [`product-portfolio-strategist`](../skills/product-portfolio-strategist/SKILL.md)
- [`reliability-modernization`](../skills/reliability-modernization/SKILL.md)
- [`knowledge-learning-architect`](../skills/knowledge-learning-architect/SKILL.md)
- [`organizational-transformation`](../skills/organizational-transformation/SKILL.md)
