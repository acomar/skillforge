# Experiência Visual de Versionamento

## Intenção
Fazer sincronização e versionamento parecerem parte natural da aplicação, não uma ferramenta separada. O usuário não precisa conhecer Git, commits, branches, HEAD, rebase ou merge de três vias.

A interface deve ser sutil, minimalista, bonita e previsível. No uso normal, o versionamento quase desaparece.

## Princípio central
**Silêncio quando está tudo bem, clareza quando é necessária uma ação.**

Não exibir informação técnica apenas porque ela existe.

## Nível 1: estado cotidiano
Na barra principal, reservar uma pequena área de sincronização:
- ícone de estado;
- texto curto opcional;
- ação primária contextual.

Estados:
- Atualizado
- Alterações salvas neste dispositivo
- Nova versão disponível
- Sincronizando
- Resolver diferenças
- Sem conexão
- Reconectar pasta

Não mostrar hashes, IDs, branches ou nomes internos.

## Ação principal
Preferir um único comando: **Sincronizar**.

A aplicação decide internamente se precisa obter mudanças, integrar, publicar ou apenas confirmar que está atualizada.

Ações secundárias ficam em menu discreto:
- Salvar versão
- Obter última versão
- Publicar alterações
- Ver histórico
- Configurar repositório

Mostrar somente ações aplicáveis ao estado atual.

## Feedback
Operações rápidas não abrem modal. Use mudança de estado inline, por exemplo: "Sincronizando..." e depois "Atualizado agora".

Erros recuperáveis explicam o ocorrido e oferecem uma ação, por exemplo: "Não foi possível acessar a pasta compartilhada. Reconectar".

Nunca usar códigos técnicos como mensagem principal.

## Alterações locais
Não interromper o usuário a cada salvamento. Mostrar discretamente "Alterações não sincronizadas" ou, quando útil, a quantidade de alterações, acompanhado da ação Sincronizar.

## Histórico
Histórico é secundário e abre sob demanda em drawer/painel lateral.

Cada versão mostra:
- autor quando disponível;
- data/hora amigável;
- descrição;
- resumo semântico das alterações.

Exemplo: "Ana, hoje 10:42. Atualizou 2 eventos e adicionou 1 regra."

Ações contextuais: Ver alterações e Restaurar esta versão. Detalhes técnicos ficam em área avançada.

## Nova versão remota
Sem edição local incompatível: "Nova versão disponível · Atualizar".

Com alterações locais: "Há mudanças suas e uma versão mais recente · Sincronizar".

Não mencionar rebase.

## Resolver diferenças
Esta é a única experiência que pode ocupar uma tela ou modal maior.

Cabeçalho: "Precisamos da sua decisão". Explicação: "Algumas alterações foram feitas por você e por outra pessoa no mesmo conteúdo."

Resolver uma entidade ou campo significativo por vez.

Exibir:
- contexto/nome do item;
- versão anterior quando ajudar;
- Sua alteração;
- Alteração compartilhada;
- Resultado;
- diferença destacada semanticamente.

Ações:
- Usar a minha
- Usar a compartilhada
- Combinar
- Editar resultado

Se for seguro combinar automaticamente, fazer sem interromper e registrar no resumo.

Mostrar progresso, por exemplo "Diferença 2 de 4". Permitir navegar sem perder escolhas.

Antes de publicar: "4 diferenças resolvidas" e ação "Concluir sincronização".

## Comparação
Nunca apresentar JSON bruto como experiência padrão.

Por tipo:
- texto: destaque de trechos;
- campo: antes/depois;
- entidade: propriedades modificadas;
- coleção: itens adicionados/removidos/modificados;
- ordem: posição anterior/nova;
- domínio customizado: renderer fornecido pela aplicação.

Permitir ConflictRenderer e EntityRenderer plugáveis para que cada app apresente diferenças em sua própria linguagem.

## Primeiro uso
Quando não existe repositório:
"Onde este projeto deve ser compartilhado?"
Ação: "Escolher pasta".

Depois: "Pasta conectada. As alterações poderão ser sincronizadas com quem tiver acesso a ela."

Não explicar infraestrutura interna salvo se solicitado.

## Reconexão
Se a permissão expirar: "Precisamos acessar novamente a pasta compartilhada." Ação: "Reconectar".

Preservar trabalho local enquanto o acesso estiver indisponível.

## Design visual
- ocupar o mínimo possível da interface principal;
- herdar tipografia e componentes do produto;
- não criar uma segunda identidade visual para sincronização;
- sem decoração desnecessária;
- ícones simples e familiares;
- cor nunca como único indicador;
- animação somente para atividade/transição;
- respeitar prefers-reduced-motion;
- modal somente quando a tarefa bloquear o fluxo;
- histórico preferencialmente em drawer;
- resolução de diferenças em modal amplo ou página dedicada conforme complexidade;
- densidade confortável e hierarquia forte.

## Progressive disclosure
Camada 1: estado + Sincronizar.
Camada 2: histórico e ações secundárias.
Camada 3: resolução de diferenças.
Camada 4: diagnóstico técnico, somente para suporte/admin quando implementado.

## Responsividade
Desktop: estado compacto na barra, histórico em drawer, comparação lado a lado quando houver espaço.
Mobile: estado compacto, comparação empilhada e ações fixadas na parte inferior quando útil.

## Acessibilidade
- navegação por teclado;
- foco visível;
- labels acessíveis;
- estados anunciáveis por tecnologia assistiva;
- contraste adequado;
- não depender apenas de cor;
- áreas de clique confortáveis;
- escolhas reversíveis antes da conclusão.

## Estados que precisam de design
1. Atualizado.
2. Alterações locais.
3. Sincronizando.
4. Nova versão disponível.
5. Divergência auto-resolvida.
6. Diferenças exigindo decisão.
7. Offline.
8. Pasta inacessível ou permissão expirada.
9. Erro de integridade/schema.
10. Sincronização concluída.

## Anti-padrões
- toolbar cheia de comandos Git;
- modal de sucesso a cada sincronização;
- mostrar JSON para resolver diferenças;
- confirmar ações reversíveis triviais;
- badges chamativos quando tudo está normal;
- termos técnicos de Git;
- cores agressivas para estados normais;
- esconder erro crítico atrás de ícone;
- resolver automaticamente conflito ambíguo.

## Critérios de aceite
- Usuário sem conhecimento de Git sincroniza sem treinamento.
- Em Atualizado, o recurso não compete com a tarefa principal.
- Fluxo cotidiano exige no máximo uma ação explícita.
- Nenhuma diferença exige visualizar ou editar JSON.
- Usuário entende o impacto antes de concluir resolução.
- Histórico existe sem poluir a tela principal.
- Funciona com mouse, teclado e touch.
- Linguagem é de produto, não de controle de versão.
