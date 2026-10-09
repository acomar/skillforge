# Contrato da timeline e comandos reais

Python3.11+, FFmpeg e FFprobe no PATH. Todos os JSONs usam UTF-8 e schema_version1. Os scripts não dependem de serviço externo de geração, não geram voz e não executam ASR.

## Das páginas ao plano

Prefira `--analysis /projeto/entrega/editing-analysis.json` quando receber a análise exportada pelo roteirista: ela inclui roteiro/manifesto, catálogo e mapa de imagens. Não combine `--analysis` com `--manifest`/`--script`. Consulte [analise-para-edicao.md](analise-para-edicao.md) para busca, fingerprints e realocação da pasta. Depois de conferir os recortes/movimentos, `--confirm-legibility` pode registrar essa revisão no caminho `--analysis`; o alinhamento do áudio continua separado.

O manifesto e roteiro usam o contrato de evidências: manifesto com `pages[{id,file,status,reviewed,panels[{id,bbox}]}]`; roteiro com `reading_direction` e `beats[{id,narration,page_id,panel_id}]`. `status` deve ser narrative e `reviewed:true` nas páginas utilizadas. Imagens são paths relativos ao `--image-root`; sem essa opção, o diretório do manifesto é a base. O inventário da skill de roteiro cria paths relativos à pasta inventariada: passe essa pasta explicitamente como image-root.

Antes do builder, confira cada crop e movimento e registre `legibility_reviewed:true` no painel ou beat. `reviewed` de página não implica revisão dos extremos do zoom. `bbox` é normalizado XYXY, não XYWH. Hash de página, quando presente, precisa corresponder ao arquivo atual.

Marcas confirmadas por beat:

```json
{
  "schema_version": 1,
  "method": "manual",
  "confirmed": true,
  "beats": [
    {"id": "B01", "start": 0, "end": 8},
    {"id": "B02", "start": 8, "end": 18}
  ]
}
```

O exemplo supõe áudio de18s. Cada marca cobre o beat até a entrada do seguinte, inclusive pausas internas; a primeira inclui silêncio inicial e a última alcança duração do áudio. `reviewed-asr` é método permitido para **marcas de beats já revisadas**, não palavras brutas de transcrição. `--confirm-alignment` também confirma marcas lidas/revisadas; não use para promover uma previsão não conferida.

```text
python scripts/build_timeline.py --manifest /projeto/page-manifest.json --script /projeto/script.json --image-root /projeto/imagens --audio /projeto/narracao.wav --alignment /projeto/alignment.json --output /projeto/timeline.json
```

Ou, com o arquivo de análise e revisão editorial dos recortes já realizada:

```text
python scripts/build_timeline.py --analysis /projeto/entrega/editing-analysis.json --confirm-legibility --audio /projeto/narracao.wav --alignment /projeto/alignment.json --output /projeto/timeline.json
```

Para áudio com várias faixas, acrescente `--audio-stream INDEX` com índice absoluto confirmado. Sem marcas, `--draft` cria tempos estimados por peso de palavras, `readiness:draft` e `renderable:false`. Serve à prévia; exige alinhamento real antes do master. O builder nunca compara automaticamente o conteúdo falado ao texto.

Limites são quantizados em frames contínuos, total=ceil(duração_áudio×fps), erro final menor que um frame. Arquivo de saída precisa ser novo; para revisar o plano gere outro nome, preservando a versão anterior.

## Plano produzido

```json
{
  "schema_version": 1,
  "readiness": "ready",
  "renderable": true,
  "canvas": {"width": 1920, "height": 1080, "fps": "30000/1001"},
  "profile": "comic-identity-longform-v1",
  "audio": {"file": "narracao.wav", "stream_index": 0},
  "beats": [
    {
      "id": "B01",
      "start": 0,
      "end": 8.008,
      "image": "imagens/01.jpg",
      "bbox": [0.05, 0.05, 0.95, 0.4],
      "motion": {"from_scale": 1, "to_scale": 1.35, "easing": "smoothstep"},
      "transition_seconds": 0.4,
      "color_mode": "original",
      "focal_point": [0.5, 0.5],
      "legibility_reviewed": true
    }
  ]
}
```

Trecho ilustrativo, não timeline completa: beats reais precisam cobrir todo áudio. Builder acrescenta frames, duração, hashes, precisão declarada e origem. Os paths do plano são relativos ao **diretório do plano**, podendo usar `../` para referenciar mídia do projeto. Não resolva a imagem pelo cwd do terminal.

Quando presentes, `production_structure` e `section_id` são preservados no plano para o agente compor gancho, intro/vinheta, contexto, recap, análise/revelações, CTA e outro. Esses metadados não alteram tempos ou imagens e não inserem módulos silenciosos automaticamente. A composição completa e seu mix estão em [estrutura-completa-sem-anuncios.md](estrutura-completa-sem-anuncios.md).

`from_scale/to_scale` variam1–2.5 sobre fit com margem. Sem endpoints definidos, o builder alterna aproximação/afastamento usando pico entre1.25–1.50 conforme a duração alinhada: `1+min(0.50,max(0.25,0.06*segundos))`. Endpoints explícitos permanecem intactos. `motion.easing` aceita `smoothstep` (padrão, acelera/desacelera) ou `linear` (velocidade constante); valores inválidos são rejeitados. `focal_point` é relativo ao recorte. `color_mode` aceita manga_cyan ou original. Fade ocorre dentro de cada beat, sem sobreposição de duração entre beats. O renderer implementa curvas originais e fundo de imagem ou ambiente discreto; não recupera os keyframes do projeto de referência. Imagens de edição: PNG/JPG/JPEG/WebP/BMP/TIF/TIFF; GIF inventariado na leitura precisa ser convertido para imagem estática conferida.

## Validar, renderizar e retomar

```text
python scripts/render_manga.py /projeto/timeline.json --validate-only
python scripts/render_manga.py /projeto/timeline.json --preview 640x360 --output /projeto/previa.mp4 --workdir /projeto/render-work
python scripts/render_manga.py /projeto/timeline.json --output /projeto/master.mp4 --workdir /projeto/render-work --resume
```

Para validar rascunho, inclua `--preview 640x360` também no validate-only. Prévia reduz resolução, mantendo duração: crie uma timeline curta com áudio correspondente para testar só um trecho. Não é opção automática de “primeiros30s”.

Master exige plano pronto e recortes revisados. Saída MP4 nova evita substituir fontes/entregas. `--resume` reaproveita segmentos do mesmo hash e verifica probe/decode; mudança de imagem, plano ou versão invalida o que precisa ser refeito. O fundo usa tempo global para não reiniciar a cada beat. Confira [identidade-visual-da-obra.md](identidade-visual-da-obra.md) para imagem original, paleta, caminhos, hashes e opções de realocação. `story_coverage` e `duration_estimate` preservam planejamento; duração/frame count continuam sendo calculados pelo áudio efetivo. Workdir bloqueado indica render ativo ou interrupção; confira o processo antes de remover um lock residual.

Renderer normaliza áudio em duas passagens para-17LUFS/-1dBTP antes de AAC e muxa uma faixa global em48kHz estéreo192kbps. Mede novamente a entrega AAC; se o pico ultrapassar-1dBTP, aplica uma atenuação global e verifica novamente. Isso pode deixar LUFS abaixo do alvo em gravações com picos fortes. `--no-loudnorm` mantém nível fornecido; silêncio/não gated também desativa normalização com motivo no relatório.

Saídas: MP4 e `*.render-report.json` com hashes, comandos, segmentos reutilizados, limites quantizados e decode. Apenas uma faixa de áudio é usada; trilha/voz/efeitos adicionais precisam chegar em mix fornecido ou ser montados no projeto.

## Precisão do movimento

O renderer1.2.0 amplia o canvas intermediário antes de `zoompan`, inclusive posições focais, e usa `gbrap` nessa etapa para manter transparência sem subamostragem de cor. O fator adaptativo é4× em960×540 e2× em1920×1080, limitado a3840 por eixo e cerca de8,3MP; UHD usa1×. O arquivo final mantém resolução e FPS solicitados. O fundo usa a mesma precisão e tempo global, sem reiniciar o zoom em cada corte.

Esta decisão reduz os degraus causados pela janela inteira do filtro, conforme o [código oficial do FFmpeg](https://ffmpeg.org/doxygen/trunk/vf__zoompan_8c_source.html). A curva suave controla a velocidade; ela sozinha não elimina quantização espacial. Confira a saída em reprodução e preserve a evidência nos extremos do movimento. Versão, fator, curva e endpoints participam da identidade do render/cache, impedindo reutilizar segmentos da implementação antiga como se fossem novos.
