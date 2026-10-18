# Política do Motion CTA

A prioridade é a história. O motion CTA deve chegar como um gesto editorial sutil de até ~1–2s quando houver intervalo válido, e nunca atrapalhar emoção ou compreensão.

## Decisão

1. Marcar `protected:true` no ápice e, quando necessário, no respiro logo depois. Nenhum CTA invade intervalos protegidos.
2. Depois que o vídeo entrega uma resposta/acontecimento, pode caber UMA pergunta curta, específica e respondível: comentário.
3. Se o desfecho pede reconhecimento sem tristeza ou choque, curtir pode fazer sentido. Em cenas intensas preferir omitir.
4. Se há outro conteúdo relacionado e o arco terminou, seguir pode fazer sentido. Nunca pedir seguir como condição para saber o desfecho.
5. Se não há pausa semântica, deixar o CTA para descrição/comentário fixado.

## Linguagem por idioma

- `pt-BR`: `Qual momento mais te marcou?`, `O que você teria feito?`, `Siga para mais histórias`.
- `es`: `¿Qué momento te marcó más?`, `¿Tú qué habrías hecho?`, `Sígueme para más historias`.
- `en`: `Which moment stayed with you?`, `What would you have done?`, `Follow for more stories`.

Texto máximo de 56 caracteres (ideal até 34), uma linha, tom natural. Evitar som artificial de notificações, letras gigantes, loops e cartões em cima do rosto.

## Forma

Entrada e saída ~0.22s em fade + deslocamento sutil horizontal; faixa escurecida pequena e translúcida apenas para contraste. Área padrão de y 67–74% e margens laterais 10% na renderização, **sujeita à revisão** em TikTok/Reels/Shorts porque UI varia. Se ficar sobre objeto narrativo ou controles da plataforma, mudar o layout com editor adicional ou remover. A renderização básica não ajusta automaticamente a posição.

Para vídeo comum, no máximo um CTA. Dois somente com duração >=75s e duas oportunidades claramente separadas; nunca duplicar CTA apenas porque a duração permite.

Marcar `cta: [{"action":"comment", "start":30, "duration":1.6, "text":"¿Qué momento te marcó más?", "why_now":"A história já foi concluída"}]` quando confirmado na timeline real. Caso contrário, usar `cta: []`.
