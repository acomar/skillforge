---
name: ai-deep-module-design
description: Analisa interfaces e fronteiras para identificar módulos profundos, com maior comportamento por contrato simples e testes externos. Use para revisar arquitetura antes ou depois de mudanças com IA.
metadata:
  category: architecture
  status: experimental
  version: "0.1.0"
---

# AI Deep Module Design

## Princípio
Valorizar módulos coesos que encapsulam decisões complexas atrás de interface pequena, com contratos claros e testes do comportamento externo. Não confundir tamanho do arquivo com profundidade de módulo.

## Entradas
Mapa de módulos, repositório, funcionalidades em mudança, dependências, testes e métricas disponíveis.

## Processo
1. Levantar interfaces e responsabilidades reais. Identificar pontos de entrada, dependências e comportamento observado.
2. Encontrar **módulos rasos**: repassadores de chamada, abstrações sem encapsulamento, regras espalhadas e uso excessivo de detalhes internos.
3. Identificar oportunidades de fronteiras mais profundas, com comportamento significativo e contrato pequeno, preferindo alteração incremental.
4. Mapear riscos: compatibilidade, efeitos colaterais, circularidade, migração de dados, custo e mudanças em consumidores.
5. Propor interface alvo e casos externos de teste para verificar comportamento sem conhecer a implementação.
6. Priorizar por impacto, risco, esforço e possibilidade de obter feedback rápido. Nunca refatorar toda a arquitetura por impulso.
7. Para executar qualquer mudança, criar ticket com critérios e seguir `ai-tdd-execution`; revisão em `ai-independent-review`.

## Saída
`architecture-review.md`: mapa atual, pontos frágeis com evidência de arquivo, candidatos, interfaces propostas, limites, testes, benefícios e riscos.

## Sinais de conclusão
Critérios verificáveis, contratos preservados ou migração aprovada, complexidade efetivamente concentrada. Não inventar métricas nem reivindicar melhoria sem evidência.
