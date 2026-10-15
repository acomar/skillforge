# Execução, continuidade e qualidade

## Render de longa duração

Não construa centenas de filtros e entradas em um único processo por padrão. Faça um piloto que inclua fala, música, texto e uma transição. Use a menor resolução útil para revisão; faça o master somente quando conteúdo e sync estiverem corretos.

Se dividir o render, escolha fronteiras narrativas ou cortes seguros. Use handles para transições e reserve propriedade clara dos frames em cada segmento. Renderize todos os segmentos com dimensões, FPS/timebase, pixel format, codecs e parâmetros de áudio coerentes. Concat por stream copy só é adequado após conferir compatibilidade; filtros, mudanças de formato ou cortes exatos podem exigir reencoding.

Evite acúmulo de offsets: calcule posições a partir de uma timeline global. Verifique duração e junção de cada segmento, especialmente arredondamento de frames, priming de AAC e drift. Música e ambience contínuos podem ser montados como faixas globais; não reinicie a música em toda divisão computacional.

Registre checkpoint por segmento: hash das fontes relevantes, versão do plano, parâmetros/filtros, ferramentas, arquivo candidato e validação. Cache de análise não valida um render; são etapas distintas. Mudança de fonte, montagem ou preset invalida o segmento correspondente e suas transições dependentes.

## Portabilidade e falhas

Use argumentos como lista ao chamar subprocessos, sem construir shell commands a partir de nomes de arquivos. Paths de filtros FFmpeg têm regras próprias de escaping; em Windows, teste espaços, acentos e `:` de drive. Mantenha filtergraphs em arquivo quando isso melhorar clareza.

Verifique encoders com a instalação real; use `libx264` quando disponível se o hardware encoder falhar. Não substitua codec/perfil exigido pelo usuário silenciosamente. ASR é externo ao helper; se não estiver instalado, use legendas existentes ou registre a dependência que impede transcrição.

O helper tem timeout por processo. Um timeout requer diminuir capítulo/carga ou aumentar o limite conscientemente após examinar logs. Preserve falhas explícitas de probe/detector/decode. Não trate retorno não-zero como resultado vazio válido.

## Validação técnica e editorial

O subcomando `validate` confere probe, presença de vídeo, decodificação integral e duração quando informada; registra streams e checksum. Não mede loudness, inteligibilidade, lipsync ou fidelidade ao estilo.

Compare os dados do relatório ao contrato de entrega: dimensões e orientação, FPS/timebase, codec/pixel format, duração, presença e parâmetros de áudio. Tolerância de duração deve considerar o grid de frames e exigência do projeto, sem absorver truncamento de segundos indevidos.

Para áudio, se houver meta explícita, meça loudness e true peak com ferramenta disponível, normalize a mistura adequada e meça novamente. Não imponha um único LUFS para toda plataforma ou gênero. Confira fala sobre música, clipping, clicks, canais e sync no começo/meio/fim e nas junções.

Revise visualmente: legibilidade no tamanho de entrega, safe areas, legendas após remapeamento, frames pretos involuntários, letterboxing, cor e transições. Na recriação, compare trechos correspondentes em lado a lado e liste diferenças por beat; uma nota genérica de “95% semelhante” não substitui critérios observáveis.

Promova o arquivo candidato depois dos gates. Preserve uma versão anterior com nome próprio quando substituir. Entregue mídia, plano/projeto, comandos usados, evidência e relatório com pendências identificadas.
