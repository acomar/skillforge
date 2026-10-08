---
name: ddd-event-storming-pt
description: Transformar descobertas do domínio em eventos, comandos, regras e limites de contexto.
---

# Modelagem DDD por EventStorming

## Quando usar
Transformar descobertas do domínio em eventos, comandos, regras e limites de contexto.

## Procedimento
Delimite o domínio e objetivo. Extraia eventos no passado e organize uma linha do tempo. Descubra atores, comandos, políticas, sistemas externos e leituras necessárias. Explore caminhos alternativos e hotspots. Investigue invariantes e candidatos a agregados. Sugira bounded contexts somente com evidências de linguagem, modelo e responsabilidade. Valide cenários com especialistas e registre incertezas.

## Regras operacionais
- Faça perguntas objetivas quando informações decisivas estiverem ausentes.
- Diferencie fatos, inferências e recomendações.
- Explique trade-offs e restrições.
- Não invente resultados de testes, ferramentas ou pesquisas.
- Adapte a profundidade ao problema e ao tempo disponível.
- Entregue artefatos concretos e critérios de aceite.

## Entregáveis
Mapa de eventos e relações; glossário; hotspots; candidatos a agregados e bounded contexts; evidências e perguntas abertas.

## Verificação final
Eventos expressos como fatos, rastreabilidade, não confundir hipótese com decisão, cobertura de exceções e validação com domínio.

## Proveniência
Adaptação original em português baseada em conceitos gerais da referência https://github.com/yonatankarp/software-design-skills. Não é tradução integral nem distribuição do pacote original. Consulte o projeto de origem para sua implementação completa e licença aplicável.
