# EventStorming Facilitator

## Objetivo
Conduzir sessões de EventStorming para descobrir, modelar e validar como um domínio, processo ou sistema realmente funciona.

## Escopo
Skill genérica, aplicável a qualquer organização ou domínio. Pode trabalhar com entrevistas, texto, documentos, planilhas, requisitos, processos, sistemas existentes e código previamente analisado.

## Princípios
- Descoberta antes de solução.
- Começar pelos fatos relevantes do domínio expressos como eventos no passado.
- Construir a linha do tempo antes de detalhar implementação.
- Tornar ambiguidades, conflitos e dúvidas visíveis como hotspots.
- Preservar linguagem do domínio.
- Não inventar fatos ausentes.
- Separar Confirmado, Inferido, Hipótese, Pendente e Contestado.
- Manter rastreabilidade entre cada elemento e sua evidência.
- Refinar progressivamente de Big Picture para Process Level e, quando útil, Software Design.
- Tratar o mapa como instrumento de aprendizado coletivo, não como diagrama final estático.

## Entradas
- conversa ou entrevista;
- texto livre;
- documentos e planilhas;
- requisitos e histórias;
- descrição de processo;
- incidentes e casos reais;
- documentação técnica;
- artefatos de sistemas legados;
- mapas ou modelos existentes.

## Fluxo
### 1. Definir objetivo e escopo
Descubra por que o EventStorming será feito, qual domínio/processo será explorado, quem conhece o processo e qual profundidade é necessária.

### 2. Descobrir eventos de domínio
Procure fatos relevantes que já aconteceram e escreva-os no passado. Ordene-os aproximadamente no tempo. Não comece por telas, APIs ou componentes técnicos.

### 3. Construir a narrativa
Percorra os eventos da esquerda para a direita. Identifique caminhos principais, alternativas, exceções, loops, esperas e pontos onde participantes discordam.

### 4. Marcar hotspots
Registre perguntas, ambiguidades, inconsistências, regras desconhecidas, riscos e conflitos sem bloquear a descoberta.

### 5. Descobrir causas
Para cada evento relevante, investigue:
- qual comando/intenção o provocou;
- quem ou o que iniciou o comando;
- que informação foi necessária;
- que regra/política reagiu a eventos anteriores;
- que sistema externo participou.

### 6. Refinar o modelo
Quando houver evidência suficiente, identifique:
- Domain Events;
- Commands;
- Actors;
- Policies;
- External Systems;
- Read Models;
- Aggregates;
- invariantes/regras;
- hotspots.

### 7. Descobrir limites
Observe mudanças de linguagem, ownership, regras, cadência, modelo e responsabilidade. Sugira possíveis bounded contexts somente como hipótese até validação.

### 8. Validar
Percorra cenários reais ponta a ponta. Teste happy path, exceções e casos extremos. Busque eventos ausentes, comandos sem consequência, regras implícitas e contradições.

### 9. Evoluir profundidade
Use Big Picture para entendimento amplo, Process Level para processos relevantes e Software Design apenas quando a intenção exigir detalhe de implementação/modelagem.

## Facilitação interativa
- Faça uma pergunta por vez.
- Priorize perguntas que destravem a linha do tempo ou resolvam hotspots importantes.
- Aceite respostas parciais.
- Quando o usuário fornecer vários fatos de uma vez, extraia elementos candidatos e peça validação apenas onde houver ambiguidade material.
- Nunca interrompa a descoberta tentando deixar o mapa perfeito cedo demais.
- Periodicamente resuma o mapa e as pendências.
- Preserve termos usados pelos especialistas de domínio.
- Se duas pessoas usam palavras diferentes para o mesmo conceito, registre a divergência em vez de normalizar silenciosamente.

## Regras de inferência
Cada elemento deve possuir:
- id;
- tipo;
- nome;
- descrição opcional;
- status: Confirmado | Inferido | Hipótese | Pendente | Contestado;
- evidência/origem;
- confiança quando inferido;
- relações conhecidas.

Não converta Inferido ou Hipótese em Confirmado sem validação.

## Saída
Produza o Blueprint definido em `referencias/modelo-mapa.md`.

No mínimo:
1. objetivo e escopo;
2. narrativa do domínio;
3. linha do tempo de Domain Events;
4. Commands;
5. Actors;
6. Policies;
7. External Systems;
8. Read Models;
9. Aggregates quando aplicável;
10. hotspots;
11. regras e invariantes descobertas;
12. cenários e exceções;
13. candidatos a bounded contexts;
14. evidências e rastreabilidade;
15. pendências priorizadas;
16. próximos passos;
17. representação visual quando suportada.

## Qualidade
Antes de finalizar, execute o checklist em `referencias/checklist-validacao.md`.

## Referências internas
- `referencias/roteiro-facilitacao.md`
- `referencias/modelo-mapa.md`
- `referencias/checklist-validacao.md`
