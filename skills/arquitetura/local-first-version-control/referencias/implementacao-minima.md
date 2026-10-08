# Implementação mínima de referência

## Objetivo
Provar a arquitetura antes de ampliar integrações.

## Primeira prova
Construir uma aplicação HTML/TypeScript mínima com:
- IndexedDB para working copy, heads e sessão de conflitos;
- um RepositoryAdapter de teste totalmente determinístico;
- um adapter de pasta do browser somente depois que o motor passar nos testes;
- JSON com objetos contendo IDs estáveis;
- SemanticMerger com merge de três vias;
- SyncEngine sem dependência de framework;
- UI mínima com Atualizado, Alterações salvas, Sincronizar e Resolver diferenças.

## Ordem de implementação
1. Modelo e hashing.
2. LocalStore.
3. RepositoryAdapter em memória para testes.
4. criação/leitura de commits e snapshots.
5. busca de merge base.
6. diff semântico.
7. merge de três vias.
8. compare-and-swap e retry.
9. persistência de conflitos.
10. suíte de conformidade.
11. adapter real de filesystem/provider.
12. testes em browsers reais.
13. UX final.

## Definition of Done
A referência só prova a arquitetura quando:
- todos os testes de motor passam de forma determinística;
- cenários concorrentes passam repetidamente;
- nenhuma falha simulada perde working copy;
- publicação concorrente nunca usa last-write-wins silencioso;
- reautorização e fallback de pasta são testados no browser alvo;
- matriz de capacidades é preenchida com resultados reais;
- limitações são documentadas.

## Regra de expansão
Não adicionar novos providers antes de o adapter anterior passar na suíte. Cada adapter deve ser substituível sem alterar SyncEngine, SemanticMerger ou UX de domínio.
