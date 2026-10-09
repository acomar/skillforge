# Execução e qualidade

## Áudio e marcas

Probe as faixas com FFprobe antes da extração. Nas quatro referências, ambas estão marcadas default/und, mas uma é português e a outra inglês. O bitrate maior era a faixa inglesa. Confirme por conteúdo/idioma em mais de um trecho quando houver dúvida; não some essas faixas como se fossem voz e música.

Para áudio novo, transcreva a narração inteira com timestamps de palavras usando ASR local ou serviço já escolhido pelo usuário. Se um decoder tiver incompatibilidade de versão, PCM mono16k pode ser uma entrada mais simples. Transcrição fornece hipótese temporal e textual: revise nomes, palavras erradas, interrupções e intervalos sem fala. O helper de montagem não instala nem executa um ASR.

O caminho direto do builder usa marcas por beat confirmadas. O agente deve localizar no áudio o início de cada beat e criar intervalos contínuos. Não use ritmo médio de palavras para validar sincronismo. Um mapa pronto pode conter silêncio entre frases dentro do beat; não deixe lacunas de vídeo. Preserve início/fim do áudio e quantize limites em frames, com erro máximo de um frame.

## Imagem e movimento

Confira crop no começo, meio e fim. Boxes relativas à página precisam excluir cenas vizinhas quando essas cenas contradizem a fala. Um zoom2× pode ser apropriado para um rosto, mas cortar o gesto que prova a ação é falha editorial. Para leitura de balão, prefira um plano estável/menor até a fala correspondente terminar.

Fundo e ornamentos gerados são originais: transferem paleta/movimento, sem reproduzir arquivo ou logotipo da referência. Uma forma branca que cruza um rosto pode exigir reposicionamento. Não há fundamento para apagar balões da HQ por padrão.

A renderização por segmentos reduz memória, permite retomada e mantém uma única faixa de áudio contínua no mux final. Registre plan/hash e opções do render. Reuse somente segmentos do mesmo plano e mídia com decode/duração conferidos; mudança em uma imagem precisa invalidar o segmento correspondente.

## Mix e loudness

Os valores medidos pertencem ao mix português completo. Sem stems não é possível recuperar ganho separado de voz/trilha, compressor, equalizador ou música exata. Narrador e VAD não identificam instrumentos.

Como adaptação, um mix em torno de -17 LUFS e pico verdadeiro até -1 dBTP aproxima os níveis observados com margem para codec. Use medição em duas passagens quando normalizar, confira o arquivo AAC final e preserve inteligibilidade. O pico+0,1 de uma referência não é meta a copiar. O renderer não é uma estação de mixagem: se não aplicar normalização ou trilha, meça e declare o áudio usado.

Trilha fornecida pode ficar discreta sob a voz, com redução quando prejudicar compreensão; essa é recomendação editorial, não proporção de mix recuperada dos arquivos. Efeitos só em viradas que os justifiquem; não preencha toda mudança de painel com impacto.

## Verificação final

1. Validador aceita materiais e cobertura; decode completo não apresenta erros.
2. Resolução/fps/duração final conferidos; diferença vídeo-áudio ≤um frame de vídeo, com tolerância de packet/padding do codec explicitada.
3. Fluxo visual acompanha sujeito/ação/tempo da narração; abertura paga promessa e fecho tem resultado.
4. Gancho, intro/vinheta, contexto, história, análise/revelações, CTA e montagem final foram compostos e revistos. Não há propaganda/patrocínio, página de anúncio acidental, corte que destrói rosto/gesto, nem fade que deixa tela preta inexplicada. Seções declaradas só nos metadados ainda não contam como executadas.
5. Loudness e pico medidos no arquivo final; voz entendível e nenhuma outra faixa de idioma somada por acidente.
6. Informe duração renderizada, resolução da prévia, trechos revisados e diferenças do perfil.

A maturidade permanece experimental até uso editorial em masters completos. A verificação sintética dos helpers não certifica precisão das caixas ou fidelidade de uma história real.
