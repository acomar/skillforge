---
name: video-editing-shortform-manga
description: Analisa e edita Shorts, TikToks e Reels verticais de mangá, HQ e anime a partir de painéis, narração ou vídeo autorizado; escolhe um arco emocional completo, sincroniza imagens com a voz, preserva recortes em tela cheia e aplica motion CTAs discretos somente em oportunidades narrativas. Planeja, renderiza e valida entregas, sem prometer viralização.
metadata:
  category: content
  status: experimental
  version: "1.0.0"
---

# ShortForm Manga Motion, edição narrativa com retenção

## Decisão central

A história conduz o vídeo. Ritmo, foco, som e movimento servem ao momento emocional, não a uma fórmula de cortes. **CTA nunca compete com a revelação, a dor ou o ápice.** Zero CTA é melhor que um CTA intrusivo. Viralidade não é propriedade garantida de uma skill: testar o resultado no canal é obrigatório.

Esta skill é INDEPENDENTE e não modifica o editor de longos. Preserva as melhorias da versão instalada de `manga-hq-video-editor-pt` do Forge Video Studio, em especial `framing:"cover"`, `bbox` e `focal_point` revisados, zoom progressivo e suave, tela preenchida sem borda, preservação da arte e sincronização real da voz. A versão GitHub desse editor pode estar defasada: consulte o plugin instalado se estiver acessível; caso contrário use os contratos desta skill.

## Quando ativar

Pedidos para criar/editar vídeo curto de mangá/HQ/anime, produzir Shorts a partir de vídeos longos, usar quadros e narração para vídeo vertical, adicionar CTA motion sutil, ou refinar um curto existente. Não invocar para apenas gerar capa, roteiro longo ou baixar mídia.

Modos: (a) criar de páginas e áudio, (b) recortar um vídeo existente, (c) re-editar timeline fornecida, (d) analisar e recomendar sem render. Se falta mídia acessível, entregar plano verificável e declarar render pendente, nunca simular saída.

## Fluxo obrigatório

1. **Fontes e direitos.** Inventariar páginas, vídeo, áudio, idioma, duração, FPS, proporção, trilha, vozes, material original e autorização/licenças conhecidas. Direitos autorais e elegibilidade para monetização são questões diferentes. Não prometer ausência de reivindicação ou monetização. Não baixar conteúdo restrito nem publicar sem pedido.
2. **Cobertura e história.** Assistir/examinar os trechos disponíveis, mapear eventos na ordem causal e localizar: conflito, mudança de estado, ápice verdadeiro, consequência, conclusão e oportunidade real de participação. Se o material for um fragmento sem desfecho, não inventar conclusão. Adicionar narração/comentário original e transformativo quando cabível.
3. **Escolha editorial.** Construir pelo menos duas hipóteses de início baseadas na mesma evidência, comparar clareza imediata, tensão, coerência e cumprimento da promessa. Escolher duração pela história e áudio real, não pelo limite máximo da plataforma. Primeiros 1–2s já contêm ação ou conflito, sem logo ou introdução vazia.
4. **Recortes.** Criar um plano por intenção narrativa, nunca uma imagem por intervalo igual. Isolar painel usando `bbox:[x1,y1,x2,y2]` normalizado à página quando necessário; escolher `focal_point` relativo AO PAINEL. Para saída 9:16 usar `cover`: cortar proporcionalmente sem esticar e sem fundo decorativo nos planos narrativos. Rever início, meio, fim e todo movimento; nunca sacrificar rostos, mãos, balões importantes ou relação espacial. Dividir em dois planos se não couber.
5. **Áudio.** Usar a narração fornecida e preservar idioma. Alinhar tempos com áudio ouvido ou marcas conferidas. Estimativa por palavras não é sincronismo. Voz contínua; música e SFX respeitam diálogos/silêncios intencionais, sem falsos crescendos. Não exigir legendas por padrão: usar quando melhorarem a experiência e forem revisadas, no máximo duas linhas.
6. **Motion narrativo.** Parallax, aproximação, recorte, luz/sombra e transições existem para revelar informações. Não aplicar movimentos iguais mecanicamente. Se o plano já demonstra emoção, preferir silêncio visual. Preservar cores/textura da obra. A estética respeita cada mangá, sem template genérico.
7. **Motion CTA contextual.** Ler `references/motion-cta.md`. No máximo UM CTA em vídeos comuns (segundo somente com razão excepcional e duração que sustente). Escolher entre seguir, curtir ou comentar conforme a oportunidade real. Inserir após um pequeno payoff ou numa pausa semântica, jamais no primeiro gancho, em falas cruciais ou no ápice. Frase curta no idioma do vídeo, fade/slide discretos, ~1–2s, posição segura e legibilidade em celular. Se não houver momento apropriado, omitir. CTA pode estar só na legenda/pinned comment se a história pedir silêncio.
8. **Plano formal.** Gerar `short-plan.json` segundo `references/plan-example.json`; informar objetivos de cada beat, fonte, recorte, ponto focal, zoom, início/fim, proteção do clímax, texto e justificativa do CTA. Validar antes de renderizar. `scripts/shortform_render.py` implementa uma trilha executável básica para imagens/vídeo + áudio + CTA sutil; para `bbox` em páginas complexas recortar o painel primeiro, ou usar o renderer instalado, revisando 9:16. Não inventar suporte a TTS/ASR que não esteja disponível.
9. **Executar.** Primeiro vídeo piloto com material real e revisão humana; depois preview e master MP4/H.264/AAC 9:16. Usar FFmpeg/FFprobe reais. Se um motor gráfico como Remotion estiver disponível e necessário, permitir CTA vetorial equivalente, sem tornar dependência obrigatória. Registrar originais, versões, comandos e hashes; não sobrescrever mídia.
10. **Verificar.** Inspecionar frames em início/meio/fim de cada plano e assistir o master, especialmente ápice, cortes, CTA, sincronismo, música e última imagem. Probe, decode completo, orientação, duração, FPS, uma faixa de áudio e limites de pico. Validar plano e relatório; teste de mídia sintética não certifica edição narrativa. Entregar master REAL, JSON, relatório de revisão, variantes editoriais para teste A/B e copy de publicação no idioma escolhido.

## Dois caminhos de renderização

**Caminho A, preferido quando o Forge Video Studio instalado estiver acessível:** usar a versão instalada de `manga-hq-video-editor-pt`, não a versão antiga do GitHub, para construir e renderizar a timeline de painéis com `cover`, recortes de ponto focal, supersampling de movimento e normalização de áudio. Reajustar cada `bbox` e `focal_point` no canvas **9:16**; o fato de um recorte ter sido revisado em 16:9 não valida 9:16. Preparar timeline `ready` com marcas de narração verificadas e gerar `master-sem-cta.mp4`. Se houver oportunidade editorial de CTA, aplicar como pós-produção:

```bash
python scripts/motion_cta_overlay.py master-sem-cta.mp4 short-plan.json --output master.mp4
```

Este adaptador adiciona microanimação de texto sobre a master já produzida, reencodificando somente o vídeo para desenhar o overlay e mantendo o stream de áudio original sem alterar a mixagem. Não fingir equivalência de qualidade entre o editor avançado e o renderizador fallback. Se não houver momento para CTA, conservar o master sem reencode. O adaptador verifica `protected_intervals` no plano CTA, mas a marcação do clímax depende da análise editorial do agente.

**Caminho B, autônomo/fallback:** usar o renderizador incluído, que monta imagens ou clipes em 9:16 com recortes `cover`, zoom com curva suave, áudio original e CTA. É tecnicamente funcional, mas não substitui todos os módulos gráficos, supersampling e loudness da versão instalada do editor de longos.

## Motor incluído

Requisitos: Python 3.11+, FFmpeg, FFprobe; drawtext e fontconfig para overlays. Biblioteca Python padrão. Motor aceita painel já isolado em `image` ou clipe em `video`, com `source_start`, tempo de saída, foco, zoom e áudio de narração. `scripts/shortform_render.py`:
```bash
python scripts/shortform_render.py validate projeto/short-plan.json
python scripts/shortform_render.py render projeto/short-plan.json --output projeto/master.mp4 --workdir projeto/.render
```
O plano inclui `audio` obrigatório e `music` opcional. Não produz voz, não reconhece cenas automaticamente, não decide clímax e não retira copyright. O editor inteligente (agente) escolhe e revê a timeline. Validação técnica impede CTA sobre intervalo protegido; revisão humana é indispensável para semântica, recorte e segurança.

## Retenção e aprendizagem, sem falsas fórmulas

Orientações em `references/estrategia-e-avaliacao.md`. Meça no YouTube Studio: `shown in feed`, `stayed to watch` / escolheu assistir, engaged views, duração média assistida e percentual médio visualizado; compare vídeos equivalentes, evitando tratar volume de views como causa. Mensurar também comentários relevantes, compartilhamentos, seguidores por visualização e quedas do gráfico de retenção no momento do CTA. Testar hipóteses e interromper CTAs que prejudiquem a experiência. Nenhum número de segundos é garantia algorítmica.

## Política de entrega

Pacote: `master.mp4` (quando renderizado), `short-plan.json`, `edit-report.json`, `hooks.md`, `publish.md`. O relatório separa **medido**, **observado** e **hipótese**; inclui restrições de direitos conhecidas, trechos não revistos e estado `planned / rendered / validated`. Não afirmar arquivos ou vídeo final sem conferência. Para arte e recortes, usar referências visuais confiáveis e nunca confundir roteiro/transcrição com análise visual.
