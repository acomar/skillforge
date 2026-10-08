# Linguagem e mensagens da interface

## Princípios de escrita
- Falar sobre o trabalho do usuário, não sobre a tecnologia.
- Ser curto, calmo e específico.
- Não usar Git, commit, push, pull, rebase, branch, HEAD, merge conflict ou hash na experiência comum.
- Não chamar atenção quando nenhuma ação é necessária.
- Não afirmar sucesso antes da confirmação do repositório compartilhado.
- Sempre explicar se o trabalho local está seguro quando houver falha externa.

## Estados principais

| Estado interno | Rótulo visível | Mensagem opcional | Ação principal |
|---|---|---|---|
| updated | Atualizado | Tudo está sincronizado. | nenhuma |
| local_changes | Alterações salvas | Suas alterações estão salvas neste dispositivo. | Sincronizar |
| checking | Verificando... | Verificando se existe uma versão mais recente. | nenhuma |
| remote_newer | Nova versão disponível | Há alterações mais recentes disponíveis. | Atualizar |
| syncing | Sincronizando... | Combinando e publicando alterações com segurança. | nenhuma |
| needs_resolution | Ação necessária | Algumas alterações precisam da sua decisão. | Resolver |
| offline | Sem conexão | Suas alterações continuam salvas neste dispositivo. | nenhuma ou Tentar novamente |
| permission_lost | Reconectar pasta | Precisamos acessar novamente a pasta compartilhada. | Reconectar |
| sync_error | Não foi possível sincronizar | Suas alterações continuam salvas neste dispositivo. | Tentar novamente |
| integrity_error | Não é seguro sincronizar | Encontramos um problema na base compartilhada. Suas alterações locais estão preservadas. | Ver detalhes |
| completed | Atualizado | Sincronização concluída. | nenhuma |

## Estado saudável
Preferência visual:
**Atualizado**

Evitar:
- "Sincronização bem-sucedida!" permanentemente;
- modal de sucesso;
- toast a cada verificação;
- "Remote HEAD synchronized".

O estado saudável deve desaparecer visualmente na hierarquia da aplicação.

## Alterações locais
Rótulo:
**Alterações salvas**

Texto, se necessário:
**Suas alterações estão salvas neste dispositivo e ainda não foram compartilhadas.**

Ação:
**Sincronizar**

Se houver quantidade útil:
**3 alterações ainda não compartilhadas**

Evitar "3 commits ahead".

## Nova versão
Rótulo:
**Nova versão disponível**

Texto:
**Há alterações mais recentes disponíveis.**

Ação quando não houver mudanças locais:
**Atualizar**

Ação quando houver mudanças locais:
**Sincronizar**

Nunca dizer "Você está behind".

## Sincronização
Rótulo:
**Sincronizando...**

Texto opcional:
**Mantendo suas alterações e verificando as mudanças compartilhadas.**

Não mostrar passos técnicos como "fetch", "rebase", "merge" ou "push".

Ao terminar:
**Atualizado**

Toast opcional apenas se houver valor:
**Alterações sincronizadas.**

Se houve combinação automática:
**Tudo sincronizado. Alterações de outras pessoas foram combinadas com as suas.**

Essa mensagem deve ser secundária e não alarmante.

## Resolução de diferenças

### Entrada
Título:
**Precisamos da sua decisão**

Descrição:
**Você e outra pessoa alteraram o mesmo conteúdo. Escolha como ele deve ficar.**

Quando houver várias:
**Encontramos 3 diferenças que precisam da sua decisão.**

Evitar "3 conflitos de merge".

### Labels
- **Antes**
- **Sua alteração**
- **Alteração compartilhada**
- **Resultado**

Se o produto conhecer a identidade remota, pode substituir "Alteração compartilhada" por:
**Alteração de Ana**

### Ações
- **Usar a minha**
- **Usar a compartilhada**
- **Combinar**
- **Editar resultado**

Se houver autor:
- **Usar a minha**
- **Usar a de Ana**

Só oferecer Combinar quando existir combinação semanticamente válida.

### Progresso
**Diferença 2 de 4**

Resolvido:
**Resolvida**

Pendente:
**Precisa de decisão**

### Finalização
Quando todas estiverem resolvidas:
**Todas as diferenças foram resolvidas.**

Ação:
**Concluir sincronização**

Durante:
**Finalizando...**

Sucesso confirmado:
**Atualizado**

Se uma versão nova surgir enquanto o usuário resolvia:
**Há novas alterações compartilhadas. Estamos verificando se alguma decisão adicional é necessária.**

Se surgir novo conflito:
**Surgiu 1 nova diferença para revisar. Suas decisões anteriores foram mantidas.**

## Offline
Rótulo:
**Sem conexão**

Mensagem:
**Você pode continuar trabalhando. Suas alterações estão salvas neste dispositivo.**

Quando voltar:
**Conexão restaurada. Verificando atualizações...**

Não usar mensagem que sugira perda de dados quando não houve perda.

## Pasta/repositório

### Primeiro uso
Título:
**Escolha onde compartilhar este projeto**

Descrição:
**Selecione uma pasta compartilhada para manter as versões deste projeto disponíveis para sua equipe.**

Ação:
**Escolher pasta**

Depois:
**Pasta conectada**

Descrição opcional:
**As alterações poderão ser sincronizadas com quem tiver acesso a esta pasta.**

### Permissão expirada
Rótulo:
**Reconectar pasta**

Mensagem:
**Precisamos da sua autorização para acessar novamente a pasta compartilhada. Suas alterações continuam salvas neste dispositivo.**

Ação:
**Reconectar**

### Trocar pasta
Ação secundária:
**Alterar pasta compartilhada**

Antes da troca, explicar impacto e verificar alterações pendentes.

## Falhas

### Falha genérica de sincronização
Título:
**Não foi possível sincronizar**

Mensagem:
**Suas alterações continuam salvas neste dispositivo. Tente novamente quando quiser.**

Ação:
**Tentar novamente**

### Base mudou durante publicação
Não apresentar como erro se o motor puder reintegrar automaticamente.

Estado:
**Sincronizando...**

Somente se exigir nova decisão:
**Há uma nova diferença para revisar.**

### Dados incompatíveis
Título:
**Esta versão precisa de atenção**

Mensagem:
**A base compartilhada usa uma estrutura que esta versão do aplicativo não consegue sincronizar com segurança.**

Ação:
**Ver detalhes**

### Integridade
Título:
**Não é seguro sincronizar**

Mensagem:
**Encontramos um problema na base compartilhada. Nenhuma alteração local foi descartada.**

Ações:
**Ver detalhes**
**Tentar novamente**, apenas se apropriado.

## Histórico
Título:
**Histórico**

Item:
**Ana · hoje, 10:42**
**Atualizou 2 itens e adicionou 1 regra.**

Ações:
- **Ver alterações**
- **Restaurar esta versão**

Restauração:
Título: **Restaurar esta versão?**
Texto: **O estado atual será preservado no histórico e uma nova versão será criada a partir desta.**
Ações: **Cancelar** / **Restaurar**

Evitar "reset hard", "checkout" ou qualquer linguagem que sugira apagar histórico.

## Mensagens que nunca devem aparecer na interface comum
- merge conflict
- rebase
- pull
- push
- fetch
- commit
- branch
- HEAD
- detached HEAD
- fast-forward
- origin
- SHA/hash
- working tree
- dirty tree
- ours/theirs

Esses conceitos podem existir apenas em diagnóstico técnico opcional.

## Regra para notificações
Não notificar:
- autosave normal;
- verificação sem novidades;
- auto-merge rotineiro;
- sincronização em background concluída sem ação relevante.

Notificar discretamente:
- nova versão que aguarda ação;
- sincronização solicitada concluída, se feedback for necessário;
- conexão restaurada, somente se relevante.

Chamar atenção:
- decisão humana necessária;
- permissão perdida;
- falha que impede publicação;
- problema de integridade.

## Tom
A interface deve soar como um produto colaborativo simples, não como ferramenta de engenharia. Evitar culpa e dramatização. Preferir frases que respondam implicitamente a três perguntas:
1. O que aconteceu?
2. Meu trabalho está seguro?
3. Preciso fazer alguma coisa?
