# Microinterações de Sincronização

## Regra de experiência
O sistema deve comunicar o mínimo necessário. Mudanças de estado não devem interromper a tarefa principal, exceto quando uma decisão humana for indispensável para concluir uma sincronização solicitada.

## Componente persistente
Use um SyncStatus compacto integrado ao chrome da aplicação.

Ordem visual:
1. ícone;
2. texto curto quando necessário;
3. ação contextual somente quando útil.

Não usar contador, badge ou animação permanente quando o estado for saudável.

## Máquina de estados visual

### Atualizado
Visual: check discreto + "Atualizado".
Comportamento: nenhuma animação contínua e nenhum CTA obrigatório.
Após alguns segundos, o texto pode reduzir para apenas o ícone se o contexto continuar inequívoco.

### Editando / alterações locais
O autosave local não deve produzir toast a cada mudança.
Após persistência local, estado pode mudar silenciosamente para "Alterações salvas".
Se publicação não for automática, disponibilizar "Sincronizar" sem urgência visual.

### Verificando
Quando a aplicação faz uma consulta curta em background, não trocar imediatamente o estado para loading. Aplicar pequeno atraso visual para evitar flicker em operações rápidas.
Se demorar, mostrar atividade sutil: "Verificando...".

### Nova versão disponível
Se não houver risco para o trabalho atual:
- mostrar "Nova versão disponível";
- não abrir modal;
- não roubar foco;
- permitir "Atualizar" ou integrar na próxima sincronização conforme política do produto.

Se a versão puder ser incorporada automaticamente sem alterar a intenção do usuário, integrar e retornar para "Atualizado", registrando no histórico.

### Sincronizando
Após ação explícita:
- botão entra em estado ocupado;
- impedir clique duplicado;
- manter restante da aplicação utilizável sempre que seguro;
- texto "Sincronizando...";
- não mostrar etapas técnicas.

### Auto-merge concluído
Se mudanças concorrentes foram combinadas automaticamente:
- não abrir tela de merge;
- feedback breve "Sincronizado";
- opcionalmente "Alterações combinadas automaticamente" em detalhe não intrusivo;
- histórico registra a integração.

### Diferenças que exigem decisão
Se uma sincronização explícita encontra conflito:
1. terminar análise;
2. preservar working copy;
3. abrir Resolver diferenças;
4. focar no primeiro conflito;
5. nunca mostrar conflito parcialmente detectado enquanto análise ainda está em curso.

Se conflito for descoberto por verificação passiva em background, não interromper imediatamente a edição. Alterar o indicador para "Ação necessária" e abrir a resolução quando o usuário acionar a sincronização ou quando a publicação depender disso.

## Resolver diferenças

### Entrada
Transição curta, sem efeitos decorativos.
Título: "Precisamos da sua decisão".
Subtexto explica que duas pessoas alteraram o mesmo conteúdo.

### Cartão de diferença
Mostrar contexto primeiro, valores depois.

Estrutura:
- nome da entidade/campo;
- valor anterior, apenas quando útil;
- "Sua alteração";
- "Alteração compartilhada";
- prévia do "Resultado".

Ações:
- Usar a minha
- Usar a compartilhada
- Combinar, somente quando semanticamente válido
- Editar resultado, quando o tipo permitir

A opção selecionada atualiza imediatamente a prévia do resultado.

### Navegação
Mostrar "1 de N".
Anterior/Próxima preservam decisões.
Permitir revisar conflitos já resolvidos.
"Concluir sincronização" só fica disponível quando todas as decisões obrigatórias estiverem resolvidas.

### Saída sem concluir
Fechar/cancelar nunca perde escolhas nem working copy.
Persistir sessão de resolução localmente.
Estado passa a "Ação necessária".
Ao retornar, continuar de onde parou.

### Conclusão
Ao acionar "Concluir sincronização":
1. bloquear apenas controles que poderiam duplicar a conclusão;
2. mostrar "Finalizando...";
3. executar segunda verificação do remoteHead;
4. se não mudou, publicar;
5. se mudou e integração for automática, concluir normalmente;
6. se surgirem novos conflitos, manter decisões anteriores válidas e apresentar somente as novas decisões;
7. após confirmação remota, fechar a resolução e mostrar "Atualizado".

Nunca dizer "Concluído" antes da confirmação remota.

## Falhas

### Offline
Não modal.
Estado: "Sem conexão".
Mensagem contextual: "Suas alterações continuam salvas neste dispositivo."
Ao recuperar conexão, verificar estado remoto antes de publicar.

### Permissão perdida
Estado: "Reconectar pasta".
Ação: "Reconectar".
Não apagar referência/configuração nem trabalho local antes da tentativa de recuperação.

### Falha durante publicação
Não afirmar que a versão foi publicada.
Verificar remoteHead antes de tentar novamente para descobrir se a operação chegou a concluir remotamente.
Mensagem em linguagem natural com "Tentar novamente".

### Repositório incompatível ou corrompido
Não tentar corrigir silenciosamente.
Bloquear publicação, preservar local e apresentar ação segura para diagnóstico/recuperação.

## Histórico
Abrir em drawer sem trocar a tarefa principal.
Entrada/saída mantém posição e contexto do usuário.
Selecionar uma versão mostra resumo semântico.
"Restaurar" exige confirmação porque cria mudança relevante, mas restauração gera uma nova versão e não apaga histórico.

## Feedback e timing
- Evitar feedback visual para operações imperceptivelmente rápidas.
- Loading aparece somente quando a espera se torna perceptível.
- Toasts são reservados para resultados úteis, não para autosave normal.
- Mensagens transitórias não podem ser a única forma de comunicar erro que exige ação.
- Não usar animação pulsante contínua para estado normal.
- Respeitar prefers-reduced-motion.

## Teclado e acessibilidade
- Mudanças passivas de estado não roubam foco.
- Abertura de resolução por ação explícita move foco para título/primeiro conflito.
- Escolhas são operáveis por teclado.
- Ao concluir, foco retorna ao ponto lógico anterior.
- Mensagens importantes usam live region apropriada sem anunciar cada autosave.

## Cenários de microinteração obrigatórios

### Cenário A: edição normal
Atualizado -> usuário edita -> autosave local -> Alterações salvas -> Sincronizar -> Sincronizando -> Atualizado.

### Cenário B: outra pessoa publica mudança independente
Alterações salvas -> Nova versão detectada -> Sincronizar -> auto-merge -> Atualizado.
Nenhuma tela de conflito.

### Cenário C: mesmo campo alterado
Alterações salvas -> sincronização detecta divergência -> Precisamos da sua decisão -> usuário resolve -> Finalizando -> segunda verificação -> Atualizado.

### Cenário D: terceiro usuário publica durante resolução
Resolver diferenças -> usuário termina escolhas -> Finalizando -> remoteHead mudou -> reintegra -> se houver novo conflito, mostrar apenas nova decisão -> publicar -> Atualizado.

### Cenário E: internet cai
Alterações salvas -> Sem conexão -> usuário continua editando -> conexão retorna -> verificar remoto -> integrar -> Atualizado ou Ação necessária.

## Critério de qualidade
Se o usuário precisa pensar em controle de versão durante um fluxo sem conflito, a experiência está complexa demais.
