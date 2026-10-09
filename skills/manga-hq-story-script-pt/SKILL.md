---
name: manga-hq-story-script-pt
description: Escreve narração em português no estilo de recap de mangá azul a partir de páginas de HQ ou mangá e gera análise com imagens, painéis e recortes ligados ao roteiro para facilitar a edição. Use para transformar quadrinhos fornecidos em roteiro narrável e mapa de montagem; renderização pertence à skill de edição.
metadata:
  category: content
  status: experimental
  version: "0.2.0"
---

# Roteiro de HQ e mangá no padrão azul

Transforme páginas locais em uma narração original, envolvente e verificável, pronta para gravação e montagem. O perfil deriva de quatro vídeos longos: gancho imediato, relato causal em terceira pessoa, comentário emocional, tensão e revelação e pergunta final. Leia [references/padrao-manga.md](references/padrao-manga.md) para aplicá-lo; comprima a estrutura quando o usuário pedir um vídeo curto.

## Entradas e leitura

- Use pasta de imagens, escopo da história e duração/formato pedidos. Se duração faltar, escolha uma versão proporcional ao material, sem alongar com fatos inventados. Para história completa, examine todas as páginas narrativas e preserve o desfecho.
- Inventarie em ordem natural, com IDs, dimensões e hashes; use `scripts/story_project.py inventory --help`. Verifique orientação de leitura, páginas duplas e capítulos: HQ ocidental geralmente esquerda→direita; manga pode ser direita→esquerda.
- Examine visualmente todas as páginas; amplie balões decisivos e quadros pequenos. OCR localiza e confere texto, mas não prova quem fala, ordem dos painéis ou ação. Sem visão disponível, registre a limitação e obtenha leitura verificável antes de entregar roteiro factual.
- Classifique capa, narrativa, propaganda e editorial. O inventário inicial é provisório: confirme cada página utilizada com `reviewed: true`. Anúncios e personagens apresentados para edições futuras não são acontecimentos da história atual.
- Registre painéis/regiões com caixas normalizadas `[x1,y1,x2,y2]`, relativas à página inteira. Confira visualmente recortes aproximados. Diferencie presente, memória, sonho e fala sobre evento não desenhado.
- Para localizar as imagens depois, descreva cada painel com ação, personagens identificados, cenário e detalhes relevantes. Registre `description`, `characters` e `visual_tags` no manifesto, incluindo pistas como mãos feridas, chuva, biblioteca ou expressão de raiva quando realmente visíveis. Faça uma síntese por página; não preencha nomes/objetos incertos como se estivessem confirmados.

## Construção do roteiro

1. Identifique desejo, obstáculo, decisões, consequências e resultado disponível. Faça um mapa curto de evidências antes de narrar; veja [references/leitura-e-roteiro.md](references/leitura-e-roteiro.md).
2. Abra com a consequência ou contradição mais forte apoiada na fonte. Prometa sua explicação e entregue o contexto necessário logo depois. Um gancho pode antecipar resultado, mas preserva sua causa.
3. Narre ação→reação→consequência com frases claras e conectores de progressão. Perguntas e comentários unem os fatos, com intensidade proporcional à cena. Troque imagem quando mudar o foco da fala.
4. Preserve ironias, pistas e retornos relevantes. Sinalize mudança de tempo nas memórias. Distinga fato mostrado, declaração de personagem e interpretação: acusação não vira condenação; intenção não vira viagem realizada.
5. Termine pagando o gancho e mostrando o que mudou. Use uma pergunta ligada ao dilema ou próximo acontecimento disponível. Não invente um próximo capítulo para sustentar suspense.

Parafraseie os balões em texto próprio, sem transcrição extensa da HQ. Use a energia e a construção do perfil sem copiar frases, marca ou voz de um narrador específico. O recap pode ter spoilers, salvo pedido contrário.

## Entrega para gravação e montagem

Entregue `narration.txt` com **apenas o texto que deve ser falado**, sem tempos, nomes de painel, câmera ou rubricas. Entregue também `script.json` e `page-manifest.json`, conforme [references/contrato-do-projeto.md](references/contrato-do-projeto.md), com cada beat ligado ao painel que o sustenta. Notas editoriais ficam em `purpose`/evidências, nunca em `narration`.

Gere obrigatoriamente **`editing-analysis.json` e `editing-analysis.md`**: a análise que a edição usa para encontrar as imagens. Ela deve reunir catálogo pesquisável de páginas/painéis, descrições visuais e o mapa trecho narrado→arquivo→painel→recorte, com motivos de escolha e material excluído. Leia [references/analise-para-edicao.md](references/analise-para-edicao.md). O JSON inclui roteiro e manifesto para ser usado diretamente pelo editor; o Markdown facilita conferência e busca humana.

Em `editorial_notes` de cada beat, explique por que o painel sustenta a fala e qual detalhe deve permanecer visível; mantenha essas notas fora do texto narrado.

Use o helper para conferir integridade e gerar narração limpa:

```text
python scripts/story_project.py validate --help
python scripts/story_project.py build --help
```

O comando `build` exporta a narração e os dois arquivos de análise a partir do roteiro/manifesto revisados. Informe a pasta real das imagens com `--image-root` para guardar a localização no JSON. O helper inventaria, valida e organiza metadados; **não lê imagens nem escreve a história automaticamente**. Se faltarem descrições, complete a leitura visual antes de finalizar a análise; o helper apenas sinaliza a falta.

Leia a narração em voz alta ou estime duração com a cadência do perfil, registrando a estimativa. A duração final vem do áudio gravado, alinhado na edição. Não imponha 12–20 minutos a uma história que pede menos tempo.

## Conferência final

- Toda afirmação factual decisiva tem evidência identificável; nomes, causas e cronologia foram conferidos.
- Cada beat tem imagem narrativa revisada e recorte coerente; páginas excluídas não entram por acidente.
- O texto resolve a promessa inicial, evita repetição para preencher tempo e separa interpretação de fato.
- Narração limpa corresponde à concatenação dos beats; a edição não precisa adivinhar os painéis.
- A análise acompanha o roteiro atual: cada trecho tem arquivo, página, painel, descrição e caixa de recorte corretos, com pasta base resolvível. As imagens de apoio são identificadas como evidências, sem virar trocas automáticas de plano.
- Declare cobertura efetiva da leitura, dúvidas restantes e duração estimada ou medida.

Evidências de testes e maturidade em [references/origem-e-validacao.md](references/origem-e-validacao.md).
