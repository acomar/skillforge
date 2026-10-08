# Team Topologies Designer

## Objetivo
Facilitar o diagnóstico e o desenho evolutivo de topologias de times orientadas a fast flow, usando os princípios de Team Topologies.

## Escopo
Esta skill é genérica e pode ser usada em qualquer organização. Não assume uma estrutura organizacional, tecnologia ou plano estratégico específico.

## Princípios
- Otimizar o fluxo de valor, não o organograma.
- Tratar a organização como sistema sociotécnico.
- Usar carga cognitiva como restrição de desenho.
- Tornar ownership e limites explícitos.
- Minimizar handoffs e dependências desnecessárias.
- Usar os quatro tipos fundamentais de time: Stream-aligned, Platform, Enabling e Complicated Subsystem.
- Tornar explícitos os três modos de interação: Collaboration, X-as-a-Service e Facilitating.
- Tratar topologias como desenho evolutivo, não estado permanente.
- Nunca transformar hipótese em fato.

## Entradas aceitas
A skill pode começar com informação incompleta e combinar:
- respostas a questionários;
- entrevistas e conversas;
- texto livre;
- documentos e planilhas;
- descrições de times, sistemas e processos;
- mapas de dependências;
- métricas e problemas observados.

## Fluxo de trabalho
### 1. Definir o escopo
Identifique área, produto, domínio ou fluxo a analisar, objetivo da análise e restrições conhecidas.

### 2. Construir o As-Is
Descubra:
- fluxos de valor e seus usuários/clientes;
- times existentes, missão, tamanho e competências;
- ownership de sistemas, serviços, dados e componentes;
- dependências e handoffs;
- plataformas e capacidades compartilhadas;
- conhecimento especializado;
- gargalos e filas;
- carga cognitiva percebida;
- autonomia de entrega;
- modos de interação atuais.

Registre cada informação como Confirmado, Inferido, Hipótese ou Pendente e mantenha sua evidência.

### 3. Avaliar suficiência
Não desenhe o To-Be enquanto lacunas críticas puderem alterar materialmente a recomendação. Faça perguntas de follow-up priorizadas pelo impacto na decisão.

### 4. Diagnosticar
Avalie:
- alinhamento ao fluxo;
- carga cognitiva;
- clareza de ownership;
- autonomia;
- dependências e handoffs;
- adequação dos limites;
- necessidade de plataforma;
- necessidade de enabling;
- necessidade de complicated subsystem;
- adequação dos modos de interação.

### 5. Gerar hipóteses de desenho
Considere primeiro Stream-aligned Teams. Introduza Platform, Enabling ou Complicated Subsystem Teams apenas quando houver evidência e benefício explícito. Não use os quatro tipos como caixas obrigatórias.

Para cada hipótese informe:
- problema observado;
- evidências;
- mudança proposta;
- princípio de Team Topologies aplicado;
- benefício esperado;
- trade-offs;
- riscos;
- confiança;
- informação que poderia invalidá-la.

### 6. Definir interações
Para cada relação relevante entre times, escolha conscientemente Collaboration, X-as-a-Service ou Facilitating. Informe objetivo, duração esperada e condição de saída quando a interação for temporária.

### 7. Produzir o To-Be
Defina times, missões, limites, ownership, APIs/serviços oferecidos, interações e fluxo esperado.

### 8. Planejar evolução
Compare As-Is e To-Be e proponha uma sequência incremental de mudanças. Evite reorganizações big-bang quando uma evolução progressiva for possível.

## Regras de facilitação
- Faça uma pergunta por vez quando estiver conduzindo uma entrevista interativa.
- Pergunte primeiro o que tem maior poder de alterar a topologia.
- Aceite "não sei" como resposta e registre como pendência.
- Não force consenso artificial.
- Questione contradições explicitamente.
- Não prescreva quantidade de times sem evidência.
- Não confunda Platform Team com equipe de infraestrutura genérica.
- Não confunda componente tecnicamente difícil com justificativa automática para Complicated Subsystem.
- Não transforme colaboração permanente em padrão por conveniência.
- Não proponha estrutura apenas com base em tecnologias.
- Explique recomendações em linguagem adequada ao público.

## Saída
Produza o Blueprint de Team Topologies definido em `referencias/modelo-blueprint.md`.

A saída deve conter, no mínimo:
1. resumo executivo;
2. escopo e objetivo;
3. fatos, hipóteses e pendências;
4. diagnóstico As-Is;
5. fluxos de valor;
6. mapa de times e ownership atual;
7. dependências, handoffs e carga cognitiva;
8. score diagnóstico com justificativas;
9. topologia To-Be;
10. missão e limites de cada time;
11. modos de interação;
12. As-Is versus To-Be;
13. plano de transição;
14. riscos e trade-offs;
15. decisões com evidências e nível de confiança;
16. perguntas ainda abertas.

## Score
O score é um instrumento de comparação e conversa, não uma métrica oficial de Team Topologies. Sempre identifique-o como heurístico. Avalie de 1 a 5:
- alinhamento ao fluxo;
- autonomia;
- clareza de ownership;
- carga cognitiva sustentável;
- dependências/hand-offs;
- eficácia das interações;
- capacidade de fast flow.

Nunca apresente apenas a nota. Inclua evidências e justificativa.

## Referências internas
- `referencias/roteiro-diagnostico.md`
- `referencias/modelo-blueprint.md`
