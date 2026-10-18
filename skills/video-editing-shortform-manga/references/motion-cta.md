# Motion CTA que respeita a história

A função do motion CTA não é interromper a narrativa, mas aproveitar uma oportunidade que a história já criou. Use linguagem natural no idioma do vídeo. Nunca inserir automaticamente em todos os vídeos.

## Ordem de decisão

1. Existe um ápice, confissão, sacrifício, morte, despedida ou revelação sensível? Marque `protected:true` no beat correspondente e proteja também a breve reação/respiração a seguir, conforme áudio.
2. O público acaba de receber um payoff e cabe uma pergunta autêntica? **Comentar:** pergunta específica, curta e respondível. Exemplo `¿Tú habrías hecho lo mismo?` num intervalo seguro após a consequência, não sobre a ação final.
3. Uma conclusão trouxe memória, reconhecimento ou admiração? **Curtir:** opção discreta, `Si te conmovió, dale me gusta`, mas preferir `like` somente quando a frase couber sem desvalorizar o momento. Emoção forte geralmente merece nenhum overlay.
4. A história termina abrindo espaço para outra história do canal? **Seguir:** `Sígueme para más historias de One Piece` ou `Sigue para más historias` após o fechamento, não como chantagem para revelar o final.
5. Nenhum desses momentos existe? **Nenhum CTA visual**; disponibilizar uma frase opcional para comentário fixado.

## Política visual

- Preferir um CTA por vídeo; dois somente se houver >=75s e duas oportunidades separadas, com avaliação editorial explícita.
- Duração indicativa 1.2–2.0s, com entrada/saída de 0.2–0.3s, sem animação longa, grito, mão gigante, barra piscante ou som de notificação invasivo.
- Contraste suficiente, tipografia legível e uma única linha curta (até 56 caracteres, ideal <=34).
- Motion em fade + deslocamento leve (10–40px), sem salto; fundo semitransparente minimalista quando necessário. Elementos visuais discretos e editados em tela. Não emular botões oficiais/interações que não existem.
- Manter área textual aproximada entre y=20% e y=72%; overlays no y=68% a 74% dependem de conferência na plataforma. Margens laterais de no mínimo 10%, atenção especial a ícones à direita, legenda/caption embaixo e UI por aplicativo.
- Avaliar com frame real em miniatura e tela do celular. Se esconder rosto, gesto ou fala, mover ou omitir.
- Uma pergunta relevante antes de um desfecho protegido não autoriza inserir CTA durante suspense. Nunca atrasar artificialmente a resposta para forçar comentários.
- Não inventar diálogo canônico, pensamentos do personagem ou finais. Não usar chamadas com promessa enganosa ou manipulação emocional.

## Exemplo de marcação temporal

Beat B04: 16.0–22.0, `protected:true`, sacrifício/ápice.
Beat B05: 22.0–27.0, `protected:true`, reação e silêncio.
Beat B06: 27.0–33.0, reflexão original e desfecho.
CTA opcional: 30.0–31.5, `action:"comment"`, `why_now:"a reflexão encerrou o desfecho e convida avaliação própria"`. Esta é uma hipótese a conferir ouvindo o áudio. Se a frase de reflexão ocupar o intervalo, omitir.

## Política de idioma

`pt-BR`: `O que você teria feito?`, `Qual cena mais te marcou?`, `Siga para mais histórias`.
`es`: `¿Tú qué habrías hecho?`, `¿Qué momento te marcó más?`, `Sígueme para más historias`.
`en`: `What would you have done?`, `Which moment stayed with you?`, `Follow for more stories`.

Não traduzir automaticamente nomes próprios. Títulos, legenda, voz e CTA devem concordar no mesmo idioma.
