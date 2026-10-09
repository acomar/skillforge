---
name: manga-hq-video-editor-pt
description: Edita a história completa de uma HQ ou mangá, em geral 10–30 minutos, com identidade visual original da obra, gancho, intro, análise, CTA, encerramento e mix, sem anúncios. Use com roteiro, áudio, imagens e análise para montar e renderizar o padrão completo; criação do roteiro pertence à skill de roteiro.
metadata:
  category: content
  status: experimental
  version: "0.5.0"
---

# Edição narrativa com a identidade da obra

Monte a história inteira, do começo ao desfecho, em geral 10–30 minutos conforme a obra, sem anúncios: gancho, intro/vinheta, contexto, relato, análise/revelações, CTA e outro. O visual é original e derivado da identidade de cada HQ/mangá. Leia [references/identidade-visual-da-obra.md](references/identidade-visual-da-obra.md) para fundo/paleta e [references/historia-completa-e-duracao.md](references/historia-completa-e-duracao.md) para cobertura/duração; a execução dos módulos está em [references/estrutura-completa-sem-anuncios.md](references/estrutura-completa-sem-anuncios.md).

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
- Preserve cor, preto e branco e textura originais dos painéis por padrão. Isole quadros conforme a fala e preserve sua proporção. Ciano é tratamento opcional, escolhido para a identidade específica ou por pedido; não aplique a mesma coloração a todas as obras.
- Dê movimento perceptível aos quadros, alternando aproximação e afastamento com aceleração/desaceleração suaves. Use inicialmente cerca de 1↔1.25–1.50, ajustando à duração e ao foco; ampliações maiores servem a detalhes ou impacto quando mantiverem a evidência visível. Escolha `motion.easing:smoothstep` por padrão. Confira frames consecutivos em reprodução: não aceite pequenos saltos, tremor ou bordas que oscilam. O renderer trabalha em resolução intermediária maior para reduzir esses degraus; a documentação registra limites em resoluções muito altas.
- Crie fundo original por obra, com paleta, textura, iluminação e atmosfera extraídas das páginas. Use uma imagem de fundo própria com movimento lento e baixa distração; o painel narrativo deve dominar. Sem círculos, paralelogramos ou ornamentos genéricos flutuantes. Fundo ambient discreto é alternativa técnica; não substitui a direção de arte específica. Use fades para revelar esse ambiente e preserve proporção/foco.
- Produza gancho, intro/vinheta e encerramento coerentes com a mesma identidade: tipografia, textura e acentos visuais discretos escolhidos para a obra. Use a identidade do projeto ou título neutro. O outro mantém ritmo mais rápido; partículas/clarões só entram quando servirem ao clima. Shorts exigem pedido explícito.
- Não acrescente legendas narrativas por padrão: ausentes nas amostras examinadas. Balões da fonte continuam na imagem. Legendas pedidas são adaptação e precisam de conferência.
- Use `render_manga.py` como componente dos painéis, com `visual_identity.background` ou `--background-image` no builder para o fundo específico. Depois execute a composição de intro silenciosa, títulos, impactos, trilha/efeitos e outro com FFmpeg ou editor disponível. Esses módulos fazem parte da entrega padrão; metadados `production_structure` não os renderizam automaticamente. Confira cada módulo no arquivo final e registre qualquer pendência concreta.
- Exclua propaganda, patrocínio e oferta comercial, tanto dos vídeos de referência quanto das páginas da HQ. CTA de comentário, inscrição/seguir e próximos conteúdos permanece no formato.

Use áudio contínuo na montagem final; concatenar AAC reencodado por beat pode acumular atraso. A vinheta silenciosa precisa de intervalo próprio, preservando o alinhamento do restante da fala. Use trilha e efeitos fornecidos ou camadas originais simples, documentando sua origem; não atribua a música criada à referência. Meça loudness do mix completo, aplique ganho com headroom e confira a saída.

## Renderizar e revisar

Valide o plano e faça primeiro uma prévia representativa com material real. Confira identidade, contraste entre painel e fundo, cor original, textura, recortes, foco, zoom, fades, continuidade entre frames e sincronismo. Assista aos movimentos em velocidade normal, além dos frames parados. A prévia deve incluir uma cena clara, uma escura e uma de diálogo; evite tratamento que apague o traço ou concorra com a leitura. Corrija os problemas observados antes do master.

Entregue vídeo da história inteira, plano JSON, cobertura e relatório dos módulos realmente executados. Use o áudio real e a cobertura para conferir duração; não acelere, corte o desfecho ou repita imagens/falas para forçar a faixa de 10–30 minutos. Confira gancho, intro, contexto, corpo, análise/revelações, CTA, outro e mix; ausência de anúncio é requisito. Verifique decodificação completa, duração/cobertura, streams, resolução/fps, loudness e início/fim. Validação técnica não prova fidelidade narrativa: confira também se a imagem sustenta cada frase e se o escopo inteiro foi coberto.

Declare o que foi renderizado, trechos revisados e adaptações. Helpers testados com mídia sintética e prévia curta não certificam um master de 20 minutos.

Evidências de testes e maturidade em [references/origem-e-validacao.md](references/origem-e-validacao.md).
