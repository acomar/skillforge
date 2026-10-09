# Análise de referências longas

## Cobertura e retomada

Comece com capítulos de cinco minutos, ajustando ao hardware e à densidade de cortes. A divisão computacional não determina os capítulos narrativos. Uma sobreposição curta ajuda a revisar eventos nas bordas, mas o intervalo central de cada capítulo tem um único proprietário. Converta timestamps locais para globais antes de consolidar e deduplique eventos da sobreposição.

O helper salva metadados, imagens amostradas, candidatos de corte e checkpoints. Consulte `--help` e os JSONs produzidos para o contrato de campos. `--resume` reutiliza trabalho compatível; fonte ou parâmetros alterados invalidam o cache. Reexecute uma etapa com falha em vez de descrever sua lista vazia como ausência de eventos.

`analysis.json` informa status `running/complete/failed`, duração/streams em `facts`, identidade/cache e a lista `chapters`. Cada capítulo registra faixa central, janela com overlap, checkpoint, `stills` com `requested_time_seconds` e `scene_candidates` com tempo global e score. Os stills são posições de seek solicitadas, não anotações frame a frame. Checkpoints completos guardam hash/tamanho dos artefatos; a retomada confere esses arquivos antes de reutilizar.

Um encerramento forçado pode deixar `.video-workbench.lock`. Confirme que o processo anterior encerrou, remova somente esse arquivo de lock no diretório do projeto e rode com `--resume`. Para timeout, examine o log indicado e ajuste capítulo/carga ou `--timeout-seconds`; esse limite se aplica a cada subprocesso. Os relatórios públicos `probe --output` e `validate --report` recusam paths existentes: escolha um novo nome a cada versão.

Separe no relatório:

| Cobertura | O que significa |
| --- | --- |
| Processada | A ferramenta percorreu os intervalos e concluiu as etapas indicadas. |
| Visual amostrada | Um agente inspecionou as imagens amostradas. |
| Audiovisual assistida | Imagem e som foram revisados nos intervalos registrados. |
| Pendência | Falta acesso, detector falhou ou revisão ainda não ocorreu. |

Para declarar cobertura computacional integral, todos os capítulos do intervalo precisam ter sido processados com sucesso. Para declarar revisão audiovisual integral, imagem e som de todo o intervalo precisam ter sido assistidos. Revisão amostrada deve permanecer identificada. Não use “assisti ao vídeo inteiro” para imagens amostradas. Revisite cortes, fades, títulos e mudanças sonoras relevantes em faixas densas, não apenas a cada 30 segundos.

## Evidência editorial

Para cada evento, registre: ID, intervalo global, capítulo, imagem/composição, movimento, transição, fala, texto em tela, áudio, função, classe de evidência e confiança. Se a única fonte for texto sem timestamps, use parágrafo ou trecho como localizador e marque o intervalo como indisponível; não invente tempos nem detalhes audiovisuais.

- **Medida:** duração e score de corte obtidos da ferramenta; o score é candidato, não decisão final.
- **Observada:** texto legível, close, tela dividida, início audível de um efeito.
- **Interpretada:** corte aumenta tensão, plano funciona como prova, provável mudança de ato.

Para áudio, escute o trecho e confira quando necessário um waveform/espectrograma. Baixo nível pode ser ambience, não silêncio. Não confunda continuidade musical com uma batida forte, nem um detector de cena com identificação de planos sem cortes.

## Transcrição e sincronismo

Prefira legendas existentes quando correspondem à versão da mídia. Preserve seus tempos originais como tempo de fonte. Na edição, remapeie-os para tempo de saída e revise cortes que atravessam uma frase.

Em ASR por capítulos, use overlap suficiente para frases nas bordas; adicione o offset global, retire duplicatas e confira palavras de junção. Os resultados devem manter versão do modelo, idioma, fonte e intervalo. Sem alinhamento por palavra, use intervalo de frase e descreva essa resolução.

Monte um mapa macro com abertura, desenvolvimento, viradas, resets e fechamento. Calcule estatísticas de planos somente quando a detecção tiver sido revisada o suficiente; registre a amostra e exclua transições indevidas. Estatística de uma amostra não representa automaticamente uma hora inteira.
