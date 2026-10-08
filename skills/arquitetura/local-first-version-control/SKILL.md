# Local-First Version Control

## Objetivo
Projetar e implementar versionamento e sincronização confiáveis para aplicações HTML/local-first que mantêm dados estruturados no navegador e usam uma pasta compartilhada como repositório.

A semântica interna pode se inspirar em sistemas de controle de versão distribuído, mas a aplicação não deve depender de Git nem expor seus comandos ao usuário.

## Escopo desta versão
Esta versão especifica o motor e os fluxos. O layout detalhado das telas de sincronização, histórico e resolução visual de diferenças é uma etapa separada.

## Princípios
- Local-first: edição continua possível sobre a cópia local.
- JSON é dado estruturado, não texto a ser comparado por linhas.
- Objetos de domínio devem possuir IDs estáveis.
- Nunca sobrescrever silenciosamente alterações concorrentes.
- Toda publicação deve ser recuperável e auditável.
- Conflitos devem ser detectados por identidade/campo/operação.
- A resolução final deve poder ser feita pela interface, nunca exigir edição manual do JSON.
- O storage remoto é substituível por adapter.
- O usuário pode escolher uma pasta compartilhada como repositório quando a plataforma permitir.
- Falha de rede, perda de permissão ou indisponibilidade do diretório não pode destruir alterações locais.

## Modelo conceitual
### Working Copy
Estado editável atual mantido localmente, preferencialmente em IndexedDB.

### Repository
Estrutura persistida na pasta compartilhada. Não trate um único JSON mutável como todo o repositório.

Estrutura conceitual:

```
repository/
  manifest.json
  refs/
    main.json
  commits/
    <commit-id>.json
  snapshots/
    <snapshot-id>.json
```

Implementações podem compactar ou adaptar essa estrutura, desde que preservem as garantias.

### Manifest
Inclui versão do formato, repositoryId, schemaVersion e metadados necessários para compatibilidade.

### Commit
Deve conter no mínimo:
- id determinístico ou criptograficamente forte;
- parent/parents;
- snapshot ou referência ao snapshot;
- timestamp;
- autor/identidade quando disponível;
- mensagem opcional;
- schemaVersion;
- hash/integridade.

### Ref
Ponteiro para a versão publicada atual, equivalente conceitualmente à ponta da linha principal.

## Estados locais
Mantenha explicitamente:
- baseCommit: versão remota da qual a cópia local deriva;
- localHead: último commit local;
- workingCopy: estado atual;
- dirty: alterações ainda não salvas como versão local;
- remoteHead: última versão remota conhecida;
- syncState: atualizado | alterações-locais | remoto-mais-novo | divergente | conflitos | offline | acesso-perdido.

## Operações internas
### Salvar versão local
1. Validar schema.
2. Calcular diff semântico em relação ao localHead.
3. Se não houver mudança, não criar commit vazio por padrão.
4. Criar snapshot/commit local.
5. Atualizar localHead.
6. Não publicar automaticamente, salvo política explícita da aplicação.

### Obter estado remoto
1. Acessar o adapter configurado.
2. Ler manifest e ref principal.
3. Validar repositoryId, schemaVersion e integridade.
4. Atualizar remoteHead sem alterar a working copy.

### Sincronizar
1. Persistir com segurança alterações locais pendentes.
2. Buscar remoteHead.
3. Se localHead == remoteHead: atualizado.
4. Se remoto descende do local: fast-forward local.
5. Se local descende do remoto: publicar com proteção contra concorrência.
6. Se ambos avançaram: encontrar merge base.
7. Executar merge de três vias Base/Local/Remote.
8. Se não houver conflito: criar commit integrado e tentar publicar.
9. Se houver conflito: persistir sessão de conflito e bloquear publicação até resolução.
10. Antes da escrita final, verificar novamente remoteHead. Se mudou, reiniciar integração em vez de sobrescrever.

## Concorrência
A publicação precisa de compare-and-swap lógico:
- ler remoteHead esperado;
- preparar novo commit;
- publicar objetos imutáveis;
- atualizar a ref somente se ela ainda apontar para o head esperado.

Se o storage não oferecer escrita condicional/lock confiável, o adapter deve usar uma estratégia segura compatível com a plataforma e reconhecer explicitamente suas limitações. Nunca implementar last-write-wins silencioso como solução de concorrência.

## Diff semântico JSON
Compare por estrutura e identidade:
- objeto: campos adicionados, removidos e alterados;
- coleção identificável: itens por ID estável, não por posição;
- coleção ordenada: distinguir mudança de ordem de mudança de conteúdo;
- valores escalares: before/after;
- remoção versus alteração concorrente deve ser conflito potencial.

Permita configuração de:
- idFields;
- campos ignorados;
- campos derivados;
- coleções tratadas como conjuntos;
- estratégias específicas por path/tipo.

## Three-way merge
Entrada:
- Base: ancestral comum;
- Local: resultado local;
- Remote: resultado publicado.

Auto-merge quando:
- somente um lado alterou;
- lados alteraram campos independentes;
- ambos produziram exatamente o mesmo valor;
- regra determinística específica do domínio declara combinação segura.

Gerar conflito quando:
- mesmo campo mudou para valores diferentes;
- um lado remove e outro altera;
- movimentos/ordenação são incompatíveis;
- duas operações estruturais não podem ser combinadas com segurança;
- regra customizada indicar necessidade de decisão humana.

Nunca escolher Local ou Remote arbitrariamente.

## Conflict Model
Cada conflito deve ser dado estruturado:
- conflictId;
- entityId/path;
- tipo;
- baseValue;
- localValue;
- remoteValue;
- operações detectadas;
- contexto semântico disponível;
- opções válidas;
- resolução escolhida;
- status.

A camada visual futura consumirá esse modelo para oferecer manter local, manter remoto, combinar ou editar resultado, quando aplicável.

## Histórico e recuperação
- Commits e snapshots publicados são imutáveis.
- Deve ser possível reconstruir qualquer versão válida.
- Reverter cria nova versão, não apaga histórico.
- Detectar corrupção/hash inválido.
- Prever garbage collection somente para objetos comprovadamente inalcançáveis e nunca como requisito para operação normal.

## Schema evolution
Cada snapshot/commit carrega schemaVersion.
Defina migrations determinísticas entre versões suportadas.
Nunca sincronize estruturas incompatíveis silenciosamente.

## Repository Adapter
Interface conceitual:
- connect/selectRepository
- readManifest
- readRef
- readObject
- writeImmutableObject
- compareAndSetRef ou mecanismo equivalente
- checkPermission
- reconnect

Adapters possíveis:
- File System Access API/pasta escolhida pelo usuário;
- pasta sincronizada por OneDrive/SharePoint;
- Google Drive ou provider equivalente;
- API/servidor;
- GitHub, quando apropriado.

Não assuma que um browser preservará indefinidamente permissão a uma pasta. Implemente reconexão e tratamento de acesso perdido.

## Segurança e robustez
- Escritas atômicas quando suportadas.
- Validar JSON e schema antes de promover refs.
- Nunca executar conteúdo vindo do JSON.
- Não armazenar credenciais dentro do repositório.
- Fazer backup/recuperação antes de migrations destrutivas.
- Testar interrupção durante escrita e sincronização.
- Manter working copy íntegra mesmo se o remoto falhar.

## Testes obrigatórios
1. Primeiro repositório vazio.
2. Alteração somente local.
3. Alteração somente remota.
4. Fast-forward.
5. Dois usuários alterando campos diferentes do mesmo objeto.
6. Dois usuários alterando o mesmo campo.
7. Delete versus update.
8. Adição concorrente com IDs diferentes.
9. Colisão de ID.
10. Alteração de ordem.
11. Remote muda durante publicação.
12. Browser offline durante sync.
13. Permissão da pasta revogada.
14. JSON remoto inválido/corrompido.
15. Migração de schema.
16. Recuperação/revert.
17. Reinício do browser com alterações não publicadas.
18. Repositório aberto por duas abas.

## Critérios de aceite
- Nenhuma alteração válida é perdida silenciosamente.
- Concorrência não usa last-write-wins silencioso.
- Merge usa ancestral comum.
- Diff opera semanticamente sobre JSON.
- Conflitos ficam persistidos como estrutura consumível pela UI.
- Histórico é reproduzível.
- Storage pode ser trocado por adapter.
- O motor funciona sem exigir Git instalado.
- Falhas remotas não destroem trabalho local.

## Fora do escopo desta etapa
- Layout e design visual das telas.
- Terminologia final dos botões e mensagens.
- Componentes de diff/merge visuais.
- Design da timeline de histórico.

Esses itens pertencem à segunda camada de UX.


## Protocolo de edição concorrente

Quando duas ou mais pessoas editam simultaneamente, siga esta ordem obrigatória.

### 1. Edição não bloqueante
Cada usuário edita sua working copy local. Alterações são persistidas localmente sem disputar escrita no repositório compartilhado a cada interação. Nunca exigir lock exclusivo como fluxo normal.

### 2. Sincronização do primeiro publicador
Ao sincronizar:
1. Persistir mudanças locais pendentes.
2. Ler o remoteHead atual.
3. Se o remoteHead ainda for o baseCommit do usuário, criar/publicar os objetos imutáveis.
4. Promover a ref compartilhada usando proteção contra concorrência.
5. Confirmar o novo head.

### 3. Sincronização de outro usuário com base antiga
Se outro usuário começou da mesma base, mas encontra um remoteHead mais novo:
1. Não sobrescrever o remoto.
2. Encontrar o merge base.
3. Executar merge Base/Local/Remote.
4. Integrar automaticamente mudanças independentes e combinações comprovadamente seguras.
5. Se não houver conflito, criar uma nova versão integrada.
6. Se houver conflito, persistir a sessão e solicitar somente as decisões necessárias.

### 4. Resolução humana
Para cada conflito, preservar Base, Local e Remote. A camada visual oferece opções semanticamente válidas, como manter a alteração local, manter a compartilhada, combinar ou editar o resultado. Nenhuma escolha é publicada antes da conclusão da sessão.

### 5. Segunda verificação obrigatória
Depois da resolução e imediatamente antes de promover a nova versão:
1. Ler novamente o remoteHead.
2. Comparar com o head usado na integração.
3. Se não mudou, publicar usando compare-and-swap ou proteção equivalente.
4. Se mudou, não sobrescrever. Reintegrar contra o novo head.
5. Mostrar ao usuário apenas novos conflitos reais que surgirem.

### 6. Finalização
Após publicação confirmada:
- baseCommit = remoteHead publicado;
- localHead = remoteHead publicado;
- working copy = estado integrado;
- limpar conflitos resolvidos e dirty state aplicável;
- manter histórico;
- informar estado Atualizado.

## Regras de ouro da concorrência
1. Nunca bloquear o trabalho normal de outro usuário.
2. Nunca sobrescrever silenciosamente uma versão compartilhada.
3. Nunca pedir decisão humana para mudanças que podem ser combinadas com segurança.
4. Nunca considerar a publicação concluída antes de confirmar a promoção da ref.
5. Uma mudança remota durante resolução ou publicação sempre força nova verificação.
6. Falha de sincronização nunca descarta a working copy local.
7. A interface não expõe a complexidade do protocolo quando nenhuma ação do usuário é necessária.

## Cenário canônico
Usuários A e B partem da versão 10.

Se A altera entidade X e B altera entidade Y:
- A publica versão 11.
- B encontra 11, integra sua mudança sobre ela e publica versão 12.
- O usuário B recebe apenas confirmação de sincronização.

Se A e B alteram o mesmo campo para valores diferentes:
- A publica 11.
- B encontra 11 e o merge gera conflito.
- B resolve visualmente.
- O motor verifica novamente o remoteHead.
- Se continuar 11, publica 12.
- Se já existir uma nova versão, reintegra antes de publicar.

Este cenário é teste obrigatório de conformidade da implementação.


## Recuperação de acesso à pasta compartilhada

A implementação deve distinguir **identidade/localização da pasta** de **permissão do navegador**. Perder permissão não significa que a pasta deixou de ser conhecida.

### Estado 1: pasta conhecida e acesso válido
- Reutilizar o handle/referência persistida.
- Operar normalmente.
- Não pedir seleção nem autorização desnecessária.

### Estado 2: pasta conhecida e permissão ausente
Este é o fluxo preferencial de recuperação.

1. Recuperar o handle/referência persistida da pasta.
2. Consultar o estado de permissão suportado pela plataforma.
3. Se a referência continua válida mas a permissão não está concedida, **não abrir o seletor de diretório**.
4. Mostrar ação: **Permitir acesso**.
5. A partir de uma ação explícita do usuário, solicitar novamente a permissão para a pasta já conhecida, conforme as regras do navegador.
6. Após autorização, validar o repositoryId/manifest antes de sincronizar.
7. Retomar a sincronização pendente sem exigir que o usuário procure a pasta.

Mensagem recomendada:
**Acesso à pasta necessário**
**A pasta deste projeto já está configurada. Permita o acesso para continuar sincronizando.**
Ação: **Permitir acesso**

### Estado 3: referência da pasta perdida ou inutilizável
Somente neste caso solicitar localização novamente.

Mensagem:
**Localizar pasta compartilhada**
**Não conseguimos recuperar a referência da pasta deste projeto. Selecione-a novamente para continuar.**
Ação: **Escolher pasta**

Depois da seleção:
1. validar manifest e repositoryId;
2. se corresponder ao projeto, substituir/persistir a referência recuperada;
3. solicitar a permissão necessária;
4. sincronizar as alterações pendentes;
5. se não corresponder, não conectar silenciosamente e explicar que é outra base.

### Ordem obrigatória de fallback
**referência conhecida + acesso válido -> referência conhecida + pedir permissão -> selecionar pasta novamente**

Nunca inverter essa ordem por conveniência de implementação.

### Persistência
Quando a plataforma permitir, persistir o directory handle/referência em armazenamento apropriado, preferencialmente IndexedDB. Não assumir que essa referência ou a permissão sobreviverá indefinidamente a reinícios, limpeza de dados, mudança de navegador, políticas corporativas ou alterações do sistema.

### Regra de segurança
A recuperação de acesso nunca descarta a working copy. Enquanto a pasta estiver inacessível, continuar salvando localmente e marcar claramente que existem alterações ainda não compartilhadas.
