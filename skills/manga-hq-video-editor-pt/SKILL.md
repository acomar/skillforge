---
name: manga-hq-video-editor-pt
description: Edita vídeos de recap de HQ ou mangá com roteiro, áudio e imagens locais, usando painéis ciano, fundo azul animado, zooms, fades e sincronização da narração. Use para montar e renderizar nesse padrão; a criação do roteiro pertence à skill de roteiro.
metadata:
  category: content
  status: experimental
  version: "0.1.0"
---

# Edição de HQ e mangá no padrão azul

Monte um vídeo em que a imagem acompanha a fala: painéis isolados em ciano, fundo azul com formas e partículas, aproximações/afastamentos amplos e fades suaves. Leia [references/padrao-manga.md](references/padrao-manga.md) para valores medidos e recomendações.

## Preparar e sincronizar

Use roteiro, narração, imagens e manifesto de páginas/painéis quando disponível. Se receber somente texto, examine imagens e construa o mapa antes de escolher planos. Não distribua imagens por tempo igual sem relação com a fala.

Confira Python 3.11+, FFmpeg e FFprobe. Os helpers usam biblioteca padrão e ferramentas locais. Probe as faixas de áudio, confirme idioma/conteúdo e escolha explicitamente `stream_index`: maior bitrate ou marcação de faixa padrão não garantem a narração correta. Mantenha identidade e voz escolhidas pelo usuário.

Mapeie cada beat ao momento em que é falado no áudio real. Use marcas confirmadas por beat ou ASR com palavras e revisão de sincronismo. Veja [references/execucao-e-qualidade.md](references/execucao-e-qualidade.md).

```text
python scripts/build_timeline.py --help
python scripts/render_manga.py --help
```

O contrato está em [references/contrato-da-timeline.md](references/contrato-da-timeline.md). Estimativa por palavras pode ajudar um rascunho; não a apresente como alinhamento da gravação. Se áudio divergir do texto, ajuste o mapa ao que foi dito, sem esticar a fala para caber na previsão.

## Montar no perfil

- Base medida: 1920×1080, 16:9, 30000/1001 fps. Vertical é adaptação e exige recompor recortes.
- Corpo: luminância preto→ciano com traços/rostos legíveis. Isole quadros em vez de manter a página inteira. HQ colorida pode receber o tratamento ou preservar cor por preferência do usuário; registre a escolha.
- Alterne zoom de entrada/saída conforme o foco. Uma amostra cresce cerca de 2× em 9 segundos; use alcance amplo quando preservar a ação, reduzindo-o quando rosto/balão exigir leitura. Crop intencional pode ocorrer, sem cortar o elemento que sustenta a fala.
- Fundo azul animado e fades curtos revelando esse fundo entre planos. Preserve proporção da imagem e evite saltos de escala dentro de um beat.
- Abertura pode usar painéis coloridos e flashes discretos; marca/vinheta são opcionais, sobretudo em shorts. Montagens rápidas de encerramento não representam o ritmo do corpo de mangá.
- Não acrescente legendas narrativas por padrão: ausentes nas amostras examinadas. Balões da fonte continuam na imagem. Legendas pedidas são adaptação e precisam de conferência.
- Renderer oferece uma base reproduzível do corpo visual. Abertura especial, marca, impactos, trilha e encerramento exigem montagem/revisão quando pedidos; não declare esses elementos executados só por constarem no perfil.

Use áudio contínuo na montagem final; concatenar AAC reencodado por beat pode acumular atraso. Meça loudness do mix completo, aplique ganho com headroom e confira a saída. Não invente trilha ou efeitos como se estivessem entre os materiais recebidos.

## Renderizar e revisar

Valide o plano e faça primeiro uma prévia representativa com material real. Confira recortes, ciano, foco, extremos de zoom, fades, mudanças de página e sincronismo. Corrija problemas observados antes do master.

Entregue vídeo, plano JSON e relatório curto. Verifique decodificação completa, duração/cobertura, streams, resolução/fps, loudness e início/fim. Validação técnica não prova fidelidade narrativa: confira também se a imagem sustenta cada frase e se o escopo inteiro foi coberto.

Declare o que foi renderizado, trechos revisados e adaptações. Helpers testados com mídia sintética e prévia curta não certificam um master de 20 minutos.

Evidências de testes e maturidade em [references/origem-e-validacao.md](references/origem-e-validacao.md).
