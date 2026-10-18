---
name: video-editing-shortform-manga
description: Cria e edita Shorts, Reels e TikToks verticais com HQs/mangás, narração, quadros e vídeos acessíveis, preservando emoção, voz e enquadramento. Adiciona motion CTA sutil e oportuno de curtir, comentar ou seguir sem encobrir o clímax, renderiza e valida vídeos reais com FFmpeg.
metadata:
  category: content
  status: experimental
  version: "1.0.1"
---

# ShortForm Manga Motion

**Missão:** contar uma história completa com ritmo emocional e gerar uma montagem de alta qualidade. A meta é melhorar a retenção e a vontade de compartilhar, mas **nenhuma skill garante viralização**. A história sempre tem prioridade sobre motion e CTA.

## Origem e compatibilidade

Esta skill adapta a infraestrutura narrativa da versão INSTALADA de `manga-hq-video-editor-pt` no Forge Video Studio, não a versão antiga do repositório. Preserva o enquadramento integral `framing:"cover"`, `bbox` do painel, `focal_point` relativo ao recorte, movimento progressivo `smoothstep`, cor/textura da obra e alinhamento a narração real. A implementação do renderer de longos tem mais recursos de recorte: para painéis dentro de páginas, use o pipeline existente de análise de quadros e recorte aprovado; o renderizador de Shorts aqui incluído recebe imagem de painel isolado ou clipe. Não declara fazer sozinho segmentação inteligente, TTS, ASR ou edição por IA.

## Ativação e modos

Usar para transformar imagens, mangá, vídeo ou narração em **9:16 para Shorts, Reels e TikTok**, selecionar arco narrativo de um episódio longo, criar motion CTAs discretos e refinar vídeos existentes. Modos:

- `analysis`: assistir/examinar materiais e entregar hipóteses editoriais e plano sem render.
- `compose`: usar páginas, painel isolado, trilha e voz fornecidos.
- `extract`: encontrar trecho com começo, desenvolvimento, clímax e consequência num vídeo maior; criar timeline nova sem copiar linearmente uma faixa se a história não fechar.
- `edit`: refazer montagem existente, preservar fontes e separar tempos originais dos tempos finais.

Sem acesso real às mídias, continuar com o plano do possível e declarar `render_pending`. Não adivinhar áudio ou frames que não analisou. Jamais publicar sem autorização explícita.

## 1. Decisão editorial

1. Inventariar as fontes, idioma, relação entre imagens e narração, formato, direitos conhecidos, roteiro e edição existente. Quando houver `editing-analysis.json` do roteirista, aproveitar catálogo visual e correspondência beat/painel. Não inventar falas canon, final ou acontecimentos.
2. Descobrir **um arco humano**, com conflito visível, progressão causal, revelação/ápice e consequência. Um Short precisa satisfazer a curiosidade de quem começou. Evitar suspense artificial ou cliffhanger enganoso.
3. Propor duas aberturas honestas a partir de frames reais, escolher a mais compreensível com ação no primeiro segundo. Sem logo, vinheta, saudação ou explicação vaga no início.
4. Construir a timeline por intenção dramática, não por cortes a cada X segundos. Cortar quando o foco, a ação ou a informação mudam. Permitir pausa e silêncio quando sustentam emoção. Não alongar para perseguir duração ideal fictícia.
5. Escolher sequências que mostrem a evidência da narrativa. Em páginas, isolar cada painel com `bbox:[x1,y1,x2,y2]`; posição focal em coordenadas do painel, não da página. Nunca distribuir painéis por duração igual nem reutilizar imagem fora da fala correspondente.

## 2. Linguagem visual

- Por padrão: vertical 1080x1920, 30fps, H.264/AAC e áudio 48kHz. Painel narrativo preenche a tela sem margens nem stretch. Preserve cor ou P&B original, textura e identidade da obra.
- Antes do render recortar o painel das páginas quando necessário. A versão de curtos recebe imagens já isoladas em `image`, e clipes em `video`, com `source_start`. Para extração de painel bruto usar a infraestrutura instalada `manga-hq-video-editor-pt/scripts/build_timeline.py` ou preparação manual, não indicar que o script atual localiza o painel sozinho.
- O agente define `focus:[x,y]` do painel e `zoom:[inicio,fim]`. Escolher pontos intencionais, proteger rosto, olhar, mão, balão essencial e relação espacial. Confirmar começo, meio, fim e movimento; se não couber em 9:16, dividir o plano.
- Intercalar aproximação/afastamento suave, parallax real apenas se houver separação de camadas legítima, alteração de luz quando amparada pela arte e cortes motivados. O renderer básico faz zoom e reposicionamento, não parallax por camadas nem VFX compostos; estes exigem motor adicional se realmente necessários.
- Efeitos sonoros servem à ação e música serve ao clima; nenhuma explosão/risada/grito criado para mascarar falta de história. Não acelere falas emocionais apenas para caber no limite.
- Legendas narrativas são opcionais. Se pedidas, respeitar idioma e fala real, duas linhas curtas e margens das interfaces. Rever nomes próprios, entonação e sincronismo antes de exportar.

## 3. Motion CTAs contextuais

Leia **[motion-cta.md](references/motion-cta.md)** antes de decidir. Em geral **zero ou um CTA por vídeo**, dois apenas para >=75s quando duas oportunidades realmente existem. Proteger o beat do clímax e o respiro emocional; nenhum texto de engajamento neles. O CTA é uma frase no idioma da narração com entrada e saída discretas, aproximadamente 1–2 segundos. Pergunta verdadeira depois da conclusão -> comentar. Identificação/lembrança leve -> curtir. Próxima história, após payoff -> seguir. Quando emoção e tela não comportarem, usar texto na descrição ou comentário fixado, **não no vídeo**.

Exemplos em espanhol: `¿Qué momento te marcó más?`; `¿Tú qué habrías hecho?`; `Sígueme para más historias`. Não usar cards falsamente clicáveis nem gritos visuais. Manter texto fora de rostos e áreas de interface.

## 4. Edição executável e contrato

Produzir `short-plan.json` documentando, para cada plano: `id`, `image` OU `video`, `source_start` se vídeo, `start`, `end`, `focus`, `zoom`, `reviewed:true`, `why`, `protected`. O script verifica que há cobertura da duração total da narração, plano sem buracos ou overlaps, original presente, CTA fora de intervalo protegido, formato vertical, FPS e fontes. O agente escolhe a timeline e confirma `reviewed` somente após analisar frames, não é uma flag para contornar validação.

Exemplo completo em [plan-example.json](references/plan-example.json). Requisitos Python 3.11+ com FFmpeg/FFprobe (libx264, zoompan, drawtext). O script **não gera voz nem reconhece imagens**. Em ambientação com outros renderizadores, mantenha equivalência dos tempos e regras de clímax.

```
python scripts/shortform_render.py validate /projeto/short-plan.json
python scripts/shortform_render.py render /projeto/short-plan.json --output /projeto/master.mp4 --workdir /projeto/.shortform-work
```

Para prévia: `--preview-scale 0.5` com outro nome de saída. O script não sobrescreve um master anterior. Para vídeo vertical com áudio e música, ele monta o áudio contínuo, cria imagens em movimento e texto do CTA e valida presença de streams e decodificação. Para música com picos, voz ruim, nomes nas legendas, qualidade editorial e loudness, a inspeção humana continua necessária.

**Limitações reais:** não gera narração, SFX originais, tracking facial automático, recorte por detecção de objetos, parallax por camadas, legendas ASR nem transcrição. Tais etapas podem ser executadas por ferramentas realmente disponíveis no ambiente, nunca alegar sucesso automático.

## 5. Revisão da montagem

- Testar um piloto com abertura, clímax e CTA em material real, reproduzir em velocidade normal e testar na proporção de celular.
- Confirmar recortes em frames do início, meio e fim. Evitar cortes acidentais de testa, balões, objetos e ações.
- Confirmar que o áudio falado corresponde ao que está na tela e que o CTA não sobrepõe contexto essencial ou silêncio afetivo.
- Revisar timbre, loudness, clipping, música abaixo da fala, pontos de transição, telas negras, tempo total e decodificação integral.
- Entregar `master.mp4` APENAS se existir e tiver sido renderizado e conferido tecnicamente, `short-plan.json`, `*.edit-report.json`, hooks alternativos e roteiro/descrição para publicação, com estado `planned`, `technically_validated` ou `editorially_validated` honesto.

## 6. Pós-publicação e aprendizagem

Leia [estrategia-e-avaliacao.md](references/estrategia-e-avaliacao.md). Fazer testes A/B editoriais controlando o tema e alterando uma variável (gancho, CTA, ritmo). Não prometer sucesso viral nem inferir causalidade de poucos vídeos. Examinar sinais oficiais disponíveis: escolha de assistir vs deslizar, duração média, percentual assistido, compartilhamentos, comentários relevantes e seguidores. Se um CTA gerar queda perceptível de retenção, suprimi-lo em teste seguinte.

## 7. Originalidade e conformidade

Obras, personagens e sons de terceiros podem ter direitos autorais. Adição de zooms, legendas ou CTA por si só não garante transformação criativa suficiente nem monetização. Valor autoral precisa ser substantivo, por exemplo comentário, análise ou interpretação original, respeitando direitos e regras das plataformas. Não copiar integralmente diálogos de fãs, animes ou mangás; não fabricar fatos ou sugerir que permissionamento equivale a monetização.
