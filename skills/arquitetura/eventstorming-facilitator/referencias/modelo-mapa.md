# Blueprint do mapa EventStorming

## 1. Objetivo e escopo
Objetivo da sessão, fronteiras, profundidade e participantes/fontes.

## 2. Narrativa
Explique o fluxo em linguagem do domínio, do gatilho ao resultado.

## 3. Linha do tempo
Tabela ordenada contendo ID, Domain Event, descrição, status e evidência.

## 4. Elementos
Registre separadamente:
- Domain Events
- Commands
- Actors
- Policies
- External Systems
- Read Models
- Aggregates
- Hotspots

Cada item deve carregar status e origem.

## 5. Relações
Expresse relações como:
Actor -> Command -> Aggregate -> Domain Event
Domain Event -> Policy -> Command
Read Model -> informação usada por Actor/Command
External System <-> Command/Event

Use somente relações sustentadas pelas evidências.

## 6. Cenários
Happy path, alternativas, exceções, falhas, compensações e processos manuais.

## 7. Regras e invariantes
Regra, contexto, evidência, impacto e dúvidas relacionadas.

## 8. Bounded Context candidates
Para cada candidato: evidências de limite, linguagem, responsabilidades, eventos de integração, incertezas e confiança. Marque como hipótese até validação.

## 9. Hotspots e pendências
Ordene por impacto no entendimento/modelo. Inclua pergunta que precisa ser respondida e quais elementos ela pode alterar.

## 10. Rastreabilidade
Mantenha Elemento -> Evidência/Fonte -> Status -> Confiança.

## 11. Visualização
Quando possível, gere uma representação visual do mapa. A visualização não substitui o modelo textual estruturado.

## 12. Próximos passos
Indique o que validar, quem deveria participar e qual parte merece aprofundamento em Process Level ou Software Design.
