# Verificação e entrega

## Antes do render completo

- Confira cenário, poses e a adaptação de papel contra a prancha. Não aceitar troca de rosto, cabelo, idade ou roupa entre tomadas.
- Confira uma imagem por beat e os momentos de maior risco: ação manual, rótulo longo, close, peça pendurada, início/meio/fim de virada e final.
- Valide a projeção em 1080×1920: mãos, rostos, números e textos dentro das margens. Legenda não pode atravessar uma mão ou a informação ensinada. Mova arte, câmera ou texto e renderize novamente os quadros afetados.
- Final: coração, balão e personagens não ficam cortados nem atrás do batente quando forem o foco. Reordene profundidade e posição; não trocar o corte da imagem por uma ocultação.
- `TEXTS(t)`/readcheck ajuda nos rótulos; legendas rápidas são verificadas pelos tempos de palavra, SRT e reprodução. Uma análise estática não comprova leitura ou ritmo.

## Arquivo final

Use FFprobe e decodificação completa para conferir streams, 1080×1920, 30 fps, duração calculada e ausência de falhas. Meça loudness integrado e pico verdadeiro. Investigue black frames/silêncios como candidatos: uma abertura escura ou pausa do roteiro pode ser intencional.

Reveja o começo, todas as transições e o final; amostre a duração inteira por quadros. Quando houver reprodução com som disponível, assista ao vídeo inteiro e confira pronúncia, sync, pausas, leitura, volume e excesso de SFX. Se a revisão disponível for por quadros e medições, diga isso em `relatorio-validacao.md`; não alegar que assistiu com som.

Em conteúdo educativo de cuidado infantil, confira as afirmações e a demonstração visual com as fontes do projeto. O aviso curto “Conteúdo informativo. Não substitui a consulta.” pode aparecer nos últimos ~3 s, na zona reservada. Não adicioná-lo a um roteiro de assunto sem relação com saúde/cuidado apenas porque o canal usa esse formato.

## Pacote

Entregue em `outputs/`:

- `video.mp4`, master com voz e os efeitos efetivamente utilizados;
- `poster.jpg` ou PNG de um quadro representativo e legível;
- `legendas.srt`, com tempos reais; o SRT separado não prova que a legenda esteja queimada;
- `relatorio-validacao.md`, com checagens, cobertura perceptiva, limitações e pendências reais.

Mantenha no projeto o roteiro recebido, tratamento, storyboard, fontes usadas, alinhamento, referências, licença/créditos, código e comando de build. `work/estado.json` deve registrar a etapa, arquivos, versões e próximo passo. Não marcar `concluido` somente porque existe um MP4.

Os filmes do usuário não levam marca d'água ou crédito promocional LemoLab. Preserve atribuições de licenças quando distribuir código/fontes/ativos de terceiros; liste só os recursos realmente usados. Não alegar licença da biblioteca de SFX sem verificar o pack/termos.

Quando o pedido é criar a skill, a verificação é estrutural e dos helpers; não produzir um vídeo como requisito implícito. A skill criada não deve ser declarada homologada em produção antes de um roteiro real passar por este fluxo.
