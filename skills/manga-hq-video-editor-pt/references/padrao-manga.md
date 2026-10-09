# Perfil manga azul — evidências e aplicação

Referência histórica `manga-blue-longform-v1`, extraída originalmente na versão 0.1.0 em 2026-10-09 com `video-editing-longform-pt`. Quatro arquivos horizontais de12:49 a20:11, total68:33.369. Foram concluídos16 capítulos de análise computacional e ASR local da faixa portuguesa inteira dos quatro. A revisão visual cobriu208 amostras regulares de20s e intervalos densos de1fps em aberturas, corpo e finais. Isso não equivale a assistir continuamente todos os vídeos com imagem e som. A mesma versão deste perfil acompanha as duas skills para uso independente.


Aplicação atual `comic-identity-longform-v1`: história inteira, normalmente10–30min, sem anúncios; direção visual original por obra e cor do quadrinho preservada. O fundo azul com formas e o ciano abaixo são observações das referências, não o visual padrão atual. Leia [historia-completa-e-duracao.md](historia-completa-e-duracao.md) e [identidade-visual-da-obra.md](identidade-visual-da-obra.md).

## Roteiro e storytelling

O gancho abre com ameaça, revelação ou consequência, menciona personagem e promete explicar o capítulo. Em01 o conflito é uma derrota extrema;02 promete domínio de poder;03 anuncia confrontos e possíveis revelações;04 apresenta a origem de um personagem. A narração situa o episódio depois do gancho/vinheta e reconta ações/reações com encadeamento causal, usando terceira pessoa e passagem entre núcleos. Há comentários em primeira pessoa e teorias; marque-os como interpretação, sem transformá-los em fatos da HQ.

Nos trechos ASR, conectores de progressão são recorrentes: “então” aparece30/30/55/52 vezes. Eles ajudam continuidade, mas não devem ser copiados mecanicamente. A imagem corresponde a personagem/ação/reação e também fornece diagramas ou contexto quando a fala explica o mundo. A análise final e o fechamento usam opinião, recapitulação e chamada para próximos vídeos/comentários.

Vídeo01 tem relato até~10:19.5 e análise explícita até~12:03.3. Vídeo02 contém anúncio de navegador~31–125s e comenta possibilidades no terço final. Vídeo03 tem recapitulação depois~32.6s e análise/hipóteses no final; a abertura promete abrir o olho, enquanto o comentário final ainda fala dessa possibilidade. Vídeo04 narra origem/história, com comentário explicativo no meio e opinião depois~16:15. Copie a construção do interesse, mantendo fatos e incertezas da fonte atual; a promessa de um título não é evidência.

Em longform, gancho~20–30s + vinheta~2–4s são compatíveis com a referência. Na aplicação deste projeto, reproduza gancho, intro/vinheta, contexto, recap, comentários/análise, revelações, CTA e outro; exclua publicidade e patrocínio. A marca da vinheta pertence ao projeto, com título neutro original quando não houver identidade fornecida. Em shorts, comprima o gancho para1–5s e una funções para preservar o arco. Duração final é proporcional à história e ao áudio. O processo completo está em [estrutura-completa-sem-anuncios.md](estrutura-completa-sem-anuncios.md).

## Imagem e montagem

Canvas observado1920×1080,16:9, H.264/BT.709 a30000/1001fps. O corpo usa fundo azul royal/roxo animado, bokeh, partículas e contornos brancos de círculos/paralelogramos. Painéis isolados ficam centrados com proporção mantida; tiras horizontais, quadros verticais e close alternam conforme o foco. O zoom pode ultrapassar o canvas e recortar, mas a imagem que comprova a fala precisa permanecer visível.

No frame medido de03, papel ciano~`#50AEFF`, fundos~`#0701C7`/`#0B0068`. Não se recuperou LUT ou composição original. Ilustrações coloridas aparecem pontualmente; preservar cor nesses casos é compatível com o material. Não apagar balões por padrão: alguns scans da referência têm balões vazios, sem prova de que o editor os removeu.

Em01/02,10 intervalos completos revisados sustentam6–14s por painel; medianas das duas amostras7.5s/12.5s. Em03/04, faixas densas mostram aproximadamente8–12s. Use um beat de locução por imagem/unidade, variando por ação e legibilidade. Não há média confiável de todos os planos.

Zoom medido em03,10:11→10:20: área visível ciano cresce296→605px emframe640px, fator~2.04 em9s. Algumas referências alternam crescer/encolher; outras têm sequências de vários zooms de entrada. Na aplicação atual, prefira aproximadamente1↔1.25–1.50 com curva suave, ajustando ao tempo e ao recorte; a amplitude1.8 das versões anteriores continua uma opção para impacto quando revisada. Nas referências, trocas do corpo usam fade pela camada azul. Na aplicação atual, use aproximadamente0.2–0.3s como início ajustável para dar fluidez; esses valores são escolhas do projeto, não medições quadro a quadro do corpus.

Aberturas usam imagens coloridas, partículas e clarões; a vinheta mostra marca da referência. Encerramentos usam anime em tela cheia e montagem muito mais rápida, começando~12:04 em01,~17:17 em02,~19:47 em03 e~16:15 em04. Não use esses cortes de anime para determinar cadência de painel. Sem esse material, reproduza a função da montagem rápida com painéis fornecidos, closes e resultado da história. Use identidade e ativos do projeto; a skill pública não inclui arquivos de marca, clipes ou trilha das referências.

Não foram vistas legendas da locução nos frames inspecionados. Legendas, verticalização e manutenção de cor da HQ são adaptações possíveis por pedido do usuário.

## Áudio e cadência

Todas as fontes têm duas faixas AAC estéreo44.1kHz, default/idioma indefinido. Detecção local por conteúdo identificou português na HE-AAC~48kbps e inglês na LC~128kbps. A ordem muda no03. Maior bitrate não indica a faixa correta; as faixas são alternativas de idioma, não stems de voz/trilha.

| Vídeo | Duração(s) | FaixaPT(index absoluto) | Palavras/min(ASR) | LUFS integrado | LRA(LU) | Pico verdadeiro(dBFS) |
|---|---:|---:|---:|---:|---:|---:|
| 01 | 769.370 | 0 | 144.7 | -16.7 | 3.2 | 0.1 |
| 02 | 1061.988 | 0 | 148.4 | -17.9 | 3.0 | -0.7 |
| 03 | 1211.385 | 1 | 148.3 | -17.4 | 2.8 | -0.8 |
| 04 | 1070.626 | 0 | 151.3 | -16.4 | 2.7 | -0.0 |

Cadência do arquivo inteiro~145–151 palavras/min, incluindo anúncio/CTA. É uma contagem automática aproximada; nomes e segmentação têm erros. Default de escrita/gravação140–155ppm com pausas breves de revelação; timestamps de montagem vêm do áudio real. As medianas de contagem em janelas de1min ficam145.5/148/149/150 palavras, compatíveis com fluxo verbal constante. VAD detectou material vocal em~99% da duração, mas não separa narrador de música/efeitos.

Loudness do mix português varia-17.9 a-16.4LUFS, LRA2.7–3.2LU. Meta de adaptação~-17LUFS e pico≤-1dBTP dá margem de codificação. O pico+0.1 da referência01 não é meta recomendada. Sem stems ou audição crítica contínua, não se recuperaram trilha, equalização, compressor, timbre/prosódia exatos ou ganho separado de voz/música. Use a voz/áudio fornecidos e confira inteligibilidade; não prometa clone do locutor.

## Limites do detector e da reprodução

O limiar scene>.3 perdeu praticamente todos os fades do corpo azul e concentrou candidatos em anúncios/anime. As medianas de intervalos desses candidatos não são duração de plano. Medidas de cor/zoom vêm de frames codificados; curvas de câmera, opacidades e música originais permanecem desconhecidas.

O perfil reproduz gramática visual/narrativa observável com parâmetros originais configuráveis. Preview deve ser revisado com imagem e áudio antes do master. JSON em `perfil-manga.json` guarda medições e defaults separadamente.
