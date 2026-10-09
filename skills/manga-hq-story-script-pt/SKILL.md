---
name: manga-hq-story-script-pt
description: Conta a história inteira de uma HQ ou mangá em português, mirando 10–30 minutos conforme o material, sem anúncios, e entrega roteiro, cobertura da história, identidade visual e mapa de imagens para edição. Use para narrar quadrinhos completos com gancho, intro, análise, CTA e encerramento; renderização pertence à skill de edição.
metadata:
  category: content
  status: experimental
  version: "0.5.0"
---

# Roteiro completo de HQ e mangá

Conte a história inteira fornecida, do começo ao desfecho, mirando 10–30 minutos conforme a extensão e a complexidade da obra, sem publicidade. A estrutura reúne gancho, intro/vinheta, contexto, relato causal, comentários/análise, revelações, CTA e encerramento. Leia [references/historia-completa-e-duracao.md](references/historia-completa-e-duracao.md) para cobertura e duração e [references/estrutura-completa-sem-anuncios.md](references/estrutura-completa-sem-anuncios.md) para os módulos. Shorts são produzidos apenas por pedido explícito; o padrão é a história completa.

## Entradas e leitura

- Use a pasta inteira como escopo padrão, examine todas as páginas narrativas e preserve acontecimentos, relações causais, pistas, mudanças temporais e desfecho. Planeje 10–30 minutos de acordo com unidades narrativas e densidade de diálogo, não apenas quantidade de arquivos. Conte também as páginas duplas. Se a fidelidade pedir duração fora da faixa, registre isso; não invente nem repita eventos para preencher tempo, e não encurte omitindo o final.
- Inventarie em ordem natural, com IDs, dimensões e hashes; use `scripts/story_project.py inventory --help`. Verifique orientação de leitura, páginas duplas e capítulos: HQ ocidental geralmente esquerda→direita; manga pode ser direita→esquerda.
- Examine visualmente todas as páginas; amplie balões decisivos e quadros pequenos. OCR localiza e confere texto, mas não prova quem fala, ordem dos painéis ou ação. Sem visão disponível, registre a limitação e obtenha leitura verificável antes de entregar roteiro factual.
- Classifique capa, narrativa, propaganda e editorial. O inventário inicial é provisório: confirme cada página utilizada com `reviewed: true`. Anúncios e personagens apresentados para edições futuras não são acontecimentos da história atual.
- Registre painéis/regiões com caixas normalizadas `[x1,y1,x2,y2]`, relativas à página inteira. Confira visualmente recortes aproximados. Diferencie presente, memória, sonho e fala sobre evento não desenhado.
- Para localizar as imagens depois, descreva cada painel com ação, personagens identificados, cenário e detalhes relevantes. Registre `description`, `characters` e `visual_tags` no manifesto, incluindo pistas como mãos feridas, chuva, biblioteca ou expressão de raiva quando realmente visíveis. Faça uma síntese por página; não preencha nomes/objetos incertos como se estivessem confirmados.

## Construção do roteiro

1. Identifique desejo, obstáculo, decisões, consequências e resultado disponível. Faça um mapa curto de evidências antes de narrar; veja [references/leitura-e-roteiro.md](references/leitura-e-roteiro.md).
2. Abra com a consequência ou contradição mais forte apoiada na fonte. Prometa sua explicação, planeje a intro/vinheta do projeto e entregue o contexto logo depois. Um gancho pode antecipar resultado, mas preserva sua causa. Não intercale patrocínio, oferta comercial ou indicação de produto.
3. Narre ação→reação→consequência com frases claras e conectores de progressão. Perguntas e comentários unem os fatos, com intensidade proporcional à cena. Troque imagem quando mudar o foco da fala.
4. Preserve ironias, pistas e retornos relevantes. Sinalize mudança de tempo nas memórias. Distinga fato mostrado, declaração de personagem e interpretação: acusação não vira condenação; intenção não vira viagem realizada.
5. Termine pagando o gancho e mostrando o que mudou. Inclua comentário/análise fundamentada, pergunta ligada ao dilema e CTA breve de comentar, seguir ou assistir a outro conteúdo pertinente. Planeje a montagem visual de encerramento. Teorias ficam marcadas como hipóteses; não invente um próximo capítulo para sustentar suspense.

Parafraseie os balões em texto próprio, sem transcrição extensa da HQ. Use a energia e a construção do perfil sem copiar frases, marca ou voz de um narrador específico. O recap pode ter spoilers, salvo pedido contrário.

## Entrega para gravação e montagem

Entregue `narration.txt` com **apenas o texto que deve ser falado**, sem tempos, nomes de painel, câmera ou rubricas. Entregue também `script.json` e `page-manifest.json`, conforme [references/contrato-do-projeto.md](references/contrato-do-projeto.md), com cada beat ligado ao painel que o sustenta. Notas editoriais ficam em `purpose`/evidências, nunca em `narration`.

Gere obrigatoriamente **`editing-analysis.json` e `editing-analysis.md`**: a análise que a edição usa para encontrar as imagens. Ela deve reunir catálogo pesquisável de páginas/painéis, descrições visuais e o mapa trecho narrado→arquivo→painel→recorte, com motivos de escolha e material excluído. Leia [references/analise-para-edicao.md](references/analise-para-edicao.md). O JSON inclui roteiro e manifesto para ser usado diretamente pelo editor; o Markdown facilita conferência e busca humana.

Defina também `visual_identity` a partir da paleta, traço, gênero, cenários e clima da obra; veja [references/identidade-visual-da-obra.md](references/identidade-visual-da-obra.md). O fundo deve ser original, discreto e próprio daquela obra; preserve a arte dos painéis por padrão. Quando propuser câmera, planeje movimentos perceptíveis e suaves, com foco no detalhe narrativo; `motion.easing:smoothstep` acompanha os endpoints no arquivo de análise. A edição confirma o movimento com o áudio e os recortes reais.

Em `editorial_notes` de cada beat, explique por que o painel sustenta a fala e qual detalhe deve permanecer visível; mantenha essas notas fora do texto narrado. Registre `production_structure.sections` no roteiro e `section_id` nos beats para a edição reconhecer gancho, intro, corpo, análise, CTA e outro. Seções silenciosas, como uma vinheta, ficam no plano de produção sem criar fala ou evidência fictícia. A análise deve preservar essa estrutura junto do mapa de imagens.

Use o helper para conferir integridade e gerar narração limpa:

```text
python scripts/story_project.py validate --help
python scripts/story_project.py build --help
```

O comando `build` exporta a narração e os dois arquivos de análise a partir do roteiro/manifesto revisados. Informe a pasta real das imagens com `--image-root` para guardar a localização no JSON. O helper inventaria, valida e organiza metadados; **não lê imagens nem escreve a história automaticamente**. Se faltarem descrições, complete a leitura visual antes de finalizar a análise; o helper apenas sinaliza a falta.

Planeje a narração completa para 10–30 minutos, usando aproximadamente 140–155 palavras/min e pausas proporcionais ao drama. Uma história menor ocupa a parte curta da faixa; uma obra mais extensa ou complexa pede maior duração. A meta guia o nível de detalhe, sem autorizar omissão, fato inventado ou repetição artificial. Entregue `story_coverage` com o vínculo de todas as páginas narrativas aos beats/evidências e registre a estimativa; o áudio gravado define a duração final. Preserve os casos em que o material realmente exige menos de 10 ou mais de 30 minutos, explicando o motivo. Não divida ou transforme em short automaticamente.

## Conferência final

- Todas as páginas narrativas revisadas têm cobertura verificável no roteiro; começo, desenvolvimento e desfecho estão presentes, com duração estimada para a história inteira.
- Toda afirmação factual decisiva tem evidência identificável; nomes, causas e cronologia foram conferidos.
- Cada beat tem imagem narrativa revisada e recorte coerente; páginas excluídas não entram por acidente.
- O texto resolve a promessa inicial, evita repetição para preencher tempo e separa interpretação de fato.
- Narração limpa corresponde à concatenação dos beats; a edição não precisa adivinhar os painéis.
- A análise acompanha o roteiro atual: cada trecho tem arquivo, página, painel, descrição e caixa de recorte corretos, com pasta base resolvível. As imagens de apoio são identificadas como evidências, sem virar trocas automáticas de plano.
- A estrutura completa está planejada, com gancho, intro, contexto, história, análise/revelações, CTA e outro identificados; não há segmento publicitário. Em shorts as funções podem compartilhar o mesmo trecho.
- Declare cobertura efetiva da leitura, dúvidas restantes e duração estimada ou medida.

Evidências de testes e maturidade em [references/origem-e-validacao.md](references/origem-e-validacao.md).
