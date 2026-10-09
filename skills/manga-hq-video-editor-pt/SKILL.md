---
name: manga-hq-video-editor-pt
description: Produz vídeos completos de recap de HQ ou mangá sem anúncios, com gancho, intro, corpo azul/ciano, análise, CTA, outro e mix, a partir de roteiro, áudio, imagens e análise local. Use para montar e renderizar o padrão completo; a criação do roteiro pertence à skill de roteiro.
metadata:
  category: content
  status: experimental
  version: "0.3.0"
---

# Edição de HQ e mangá no padrão azul

Monte o vídeo completo no padrão analisado: gancho, intro/vinheta, contexto, recap, análise/revelações, CTA e montagem final, sem anúncios. Painéis ciano, fundo azul animado, zooms e fades formam o corpo; a abertura e o final têm tratamento próprio. Leia [references/padrao-manga.md](references/padrao-manga.md) para valores medidos e [references/estrutura-completa-sem-anuncios.md](references/estrutura-completa-sem-anuncios.md) para executar todos os módulos e compor o master.

## Preparar e sincronizar

Use roteiro, narração, imagens e **`editing-analysis.json`** quando disponível. Esse arquivo traz o catálogo visual e a ligação de cada trecho à imagem, painel e recorte; consulte `editing-analysis.md` para encontrar personagens, ações e detalhes com facilidade. O builder aceita `--analysis` para usar o roteiro e manifesto embutidos. Leia [references/analise-para-edicao.md](references/analise-para-edicao.md). Se receber somente texto, examine imagens e construa o mapa antes de escolher planos. Não distribua imagens por tempo igual sem relação com a fala.

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
- Produza gancho com imagens coloridas, partículas, aproximações e clarões discretos; em seguida uma intro/vinheta original do projeto. Use a identidade fornecida ou título neutro do episódio sobre o fundo azul. O encerramento usa montagem mais rápida com o material do projeto. Em shorts comprima a vinheta/transição e una módulos quando necessário.
- Não acrescente legendas narrativas por padrão: ausentes nas amostras examinadas. Balões da fonte continuam na imagem. Legendas pedidas são adaptação e precisam de conferência.
- Use `render_manga.py` como componente do corpo, inclusive planos narrados em cor original. Depois execute a composição de intro silenciosa, títulos, impactos, trilha/efeitos e outro com FFmpeg ou editor disponível. Esses módulos fazem parte da entrega padrão; metadados `production_structure` não os renderizam automaticamente. Confira cada módulo no arquivo final e registre qualquer pendência concreta.
- Exclua propaganda, patrocínio e oferta comercial, tanto dos vídeos de referência quanto das páginas da HQ. CTA de comentário, inscrição/seguir e próximos conteúdos permanece no formato.

Use áudio contínuo na montagem final; concatenar AAC reencodado por beat pode acumular atraso. A vinheta silenciosa precisa de intervalo próprio, preservando o alinhamento do restante da fala. Use trilha e efeitos fornecidos ou camadas originais simples, documentando sua origem; não atribua a música criada à referência. Meça loudness do mix completo, aplique ganho com headroom e confira a saída.

## Renderizar e revisar

Valide o plano e faça primeiro uma prévia representativa com material real. Confira recortes, ciano, foco, extremos de zoom, fades, mudanças de página e sincronismo. Corrija problemas observados antes do master.

Entregue vídeo completo, plano JSON e relatório dos módulos realmente executados. Confira gancho, intro, contexto, corpo, análise/revelações, CTA, outro e mix; ausência de anúncio é requisito. Verifique decodificação completa, duração/cobertura, streams, resolução/fps, loudness e início/fim. Validação técnica não prova fidelidade narrativa: confira também se a imagem sustenta cada frase e se o escopo inteiro foi coberto.

Declare o que foi renderizado, trechos revisados e adaptações. Helpers testados com mídia sintética e prévia curta não certificam um master de 20 minutos.

Evidências de testes e maturidade em [references/origem-e-validacao.md](references/origem-e-validacao.md).
