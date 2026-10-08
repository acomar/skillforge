# Matriz de capacidades

A implementação deve preencher esta matriz para cada ambiente realmente suportado. Não declarar suporte por suposição.

| Capacidade | Adapter de pasta do browser | Pasta sincronizada por provider | API/servidor | GitHub |
|---|---|---|---|---|
| Working copy local | Obrigatório | Obrigatório | Obrigatório | Obrigatório |
| Referência persistente ao repositório | Validar no browser alvo | Validar mecanismo | Configuração persistida | Configuração persistida |
| Reautorizar sem escolher pasta novamente | Validar no browser alvo | Depende do acesso local/browser | N/A/autenticação | N/A/autenticação |
| Objetos imutáveis | Sim | Sim | Sim | Sim |
| Compare-and-swap/controle de concorrência | Precisa estratégia comprovada | Precisa estratégia comprovada | Deve ser nativo ou implementado | Usar mecanismo seguro da integração |
| Detecção de mudança remota | Poll/ação do usuário conforme suporte | Provider/filesystem conforme suporte | Poll/SSE/WebSocket se disponível | API conforme integração |
| Offline | Sim, local-first | Sim, local-first | Sim, local-first | Sim, local-first |
| Multiusuário confiável | Só após teste de concorrência | Só após teste de concorrência | Sim, se CAS/transação comprovados | Só após teste da estratégia |
| Recuperação de permissão | Testar | Testar | Autenticação | Autenticação |

## Matriz de browsers

Preencher com evidência prática antes de prometer suporte:

| Browser/plataforma | Seleção de pasta | Handle persistente | Reautorização do handle | Escrita | Resultado da suíte |
|---|---|---|---|---|---|
| Chrome Desktop | A testar | A testar | A testar | A testar | Pendente |
| Edge Desktop | A testar | A testar | A testar | A testar | Pendente |
| Safari Desktop | A testar | A testar | A testar | A testar | Pendente |
| Firefox Desktop | A testar | A testar | A testar | A testar | Pendente |
| Mobile | A testar por plataforma | A testar | A testar | A testar | Pendente |

## Regra
"A testar" é intencional. A skill nunca deve converter expectativa de API em compatibilidade declarada. O suporte nasce de teste executado no ambiente alvo.

## Níveis de suporte
- **Suportado:** suíte de conformidade aprovada.
- **Parcial:** fluxo principal aprovado, com limitações documentadas.
- **Experimental:** funciona em protótipo, sem garantias completas.
- **Não suportado:** capacidade essencial ausente ou suíte reprovada.
