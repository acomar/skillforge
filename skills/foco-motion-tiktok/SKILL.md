---
name: foco-motion-tiktok
metadata:
  category: content
  status: experimental
  version: "1.0.0"
description: >
  Lê um ou mais prints do TikTok Creator Search Insights com assuntos sugeridos,
  tendências ou lacunas de conteúdo; escolhe temas alinhados ao Meu Bebê em Foco;
  produz roteiro original em português do Brasil e script técnico cena a cena para
  vídeos verticais Foco Motion 3D, com narração, câmera, animação, legendas,
  efeitos e JSON de produção. Use quando o usuário anexar prints do TikTok e pedir
  ideias, roteiro, storyboard ou script de cenas para Meu Bebê em Foco.
---

# Skill: Foco Motion TikTok

## Missão

Transformar prints do **TikTok Creator Search Insights** em **episódios originais, emocionalmente envolventes e visualmente explicativos** para o canal **Meu Bebê em Foco**, com objetivo de melhorar retenção, valor de pesquisa e potencial de remuneração, sem prometer viralização ou ganhos.

**A entrada é o print de tendência, não o roteiro pronto.** O tema sugerido é um sinal de interesse, que deve ser reinterpretado como uma pergunta real de mães, pais ou cuidadores. O conteúdo final precisa ser próprio e útil.

## Ativação

Use esta Skill quando forem enviados:
- 1 ou mais prints de “Informações de pesquisas para criadores”, incluindo abas Sugerido, Populares ou Lacuna de conteúdo;
- prints de tendências, temas e buscas do TikTok;
- pedidos como “crie o roteiro dessas tendências”, “selecione o melhor assunto” ou “gere as cenas em Foco Motion”.

Se o usuário citar um assunto específico, **priorize esse assunto** em vez de escolher outro. Quando houver vários, selecione automaticamente um tema forte e ofereça os próximos melhores. Não peça confirmação por padrão.

## Entradas e valores padrão

| Campo | Obrigatório? | Padrão |
|---|---|---|
| `prints` | Sim | Um ou mais screenshots anexados |
| `assunto_escolhido` | Não | Melhor tema aderente à marca |
| `duracao_alvo_segundos` | Não | 75 (faixa 65–85) |
| `idioma` | Não | pt-BR |
| `plataforma` | Não | TikTok, vertical 9:16 |
| `serie` | Não | Escolher entre três séries abaixo |
| `faixa_etaria` | Não | Detectar no tema; se impossível, evitar recomendações que dependem de idade |
| `fonte_conteudo` | Não | Página ou texto do Notion fornecido, se houver acesso |
| `estilo_voz` | Não | Narrador(a) empático(a), natural, seguro(a), curioso(a) |
| `variantes_gancho` | Não | 3 |
| `modo_saida` | Não | Roteiro + cenas + JSON para automação |

Se o print não estiver legível: extraia somente os tópicos efetivamente identificáveis, sinalize a incerteza e peça imagem melhor **apenas se nenhum tema aproveitável puder ser identificado**.

## Passo 1: Ler e transcrever os prints

1. Examinar visualmente cada print, sem inventar títulos, números, percentuais ou tendências.
2. Identificar aba/filtro: `Sugerido`, `Populares`, `Lacuna de conteúdo` ou `desconhecido`.
3. Para cada assunto visível, extrair:
   - `busca_exata`: grafia como aparece no print;
   - `indicador_exibido`: por exemplo `195K`, `48.5K`, se houver;
   - `variacao_exibida`: por exemplo `+218,6%`, se houver;
   - `sinal`: “teve um bom desempenho”, “lacuna de conteúdo”, etc.;
   - `confianca_leitura`: `alta`, `media` ou `baixa`.
4. Registrar a data da análise como data de leitura, **não** como data histórica da tendência, a menos que o print informe a data.
5. Distinguir **tendência/busca** de visualizações que o canal poderá ganhar. Nunca anunciar métricas de TikTok como promessa de alcance.
6. Identificar consultas duplicadas ou variantes ortográficas, preservando a busca exata para SEO.

### Seleção dos assuntos

Avaliar cada tópico qualitativamente em cinco dimensões, com nota de 0 a 5 apenas para **priorização interna**, não como índice científico:
- `aderencia_marca` (peso 30%): bebê, sono, maternidade e cuidados para familiares;
- `dor_ou_emocao` (25%): há conflito, dúvida, desejo ou identificação imediata?;
- `potencial_visual` (20%): dá para **mostrar** algo interessante com 3D e motion design?;
- `sinal_no_print` (15%): busca, tendência crescente ou lacuna claramente visível;
- `seguranca_e_originalidade` (10%): tema verificável, tratável sem sensacionalismo ou cópia.

`score = 0.30*A + 0.25*D + 0.20*V + 0.15*S + 0.10*O`, em escala 0–5. Sem valores numéricos legíveis no print, o fator `sinal_no_print` recebe nota neutra (2,5), nunca zero automaticamente. Não criar precisão ilusória na resposta: mostrar só a prioridade e o motivo principal.

**Excluir ou contextualizar** assuntos que não sejam adequados para bebês, incentivem riscos, dependam de alegações médicas não verificadas ou só atraiam um público sem relação com a marca. Se a consulta for “brinquedos para criança”, recortar por faixa etária e contexto de desenvolvimento, sem afirmar benefícios não comprovados.

Escolher **um tema para um roteiro completo** e listar no máximo três candidatos secundários. Se o usuário pediu vários episódios, produzir a quantidade solicitada.

## Passo 2: Escolher a série e o ângulo

### Série A: Por Dentro do Bebê
O que o cuidador vê por fora e o que uma animação didática consegue explicar. Ideal para sono, desenvolvimento, cólica, sonecas, mudanças de comportamento. Evitar representar hipóteses como se fossem imagens reais do cérebro/corpo.

### Série B: Maternidade Sem Filtro
Micro-história original de uma rotina familiar, com problema, identificação, virada e fechamento. Nunca fingir que uma dramatização de IA seja testemunho real.

### Série C: Na Prática, Mãe!
Uma ação demonstrável, um erro comum (somente quando justificável) e uma solução prática, adaptada à idade. Ideal para organização, cuidados e atividades seguras.

**Fórmula narrativa:** `SITUAÇÃO ESPECÍFICA → PERGUNTA → DESCOBERTA VISUAL → AÇÃO PRÁTICA → ALÍVIO/CLAREZA`.

Gerar **3 ganchos distintos** antes de escolher o melhor:
- `contraste`: mostrar algo contraintuitivo mas verdadeiro;
- `identificacao`: cena familiar cotidiana;
- `curiosidade`: uma pergunta respondida pelo episódio.

Proibido começar com “Olá pessoal”, “Hoje vou te ensinar”, logotipo, tela de título parada, pergunta genérica desacompanhada de ação ou promessa milagrosa. **A primeira imagem deve contar a história mesmo sem áudio.**

## Passo 3: Pesquisa e verificação

- Se existir material relevante do Notion do Meu Bebê em Foco acessível na conversa ou via conector, usá-lo **como base de assuntos e contexto**, nunca como autorização para copiar transcrições de terceiros.
- Em temas de saúde ou segurança infantil, verificar recomendações atuais com fontes médicas ou públicas confiáveis **quando a navegação estiver disponível**, priorizando sociedades pediátricas e órgãos oficiais. Se não houver verificação possível, redigir de forma conservadora e marcar afirmações que exigem revisão humana.
- Informar a faixa etária sempre que ela afetar a orientação. Não prescrever medicações, diagnósticos, técnicas de risco ou prometer resultados (“dorme a noite toda em 14 noites”) sem sustentação.
- Para sono seguro em bebês: posição inicial de barriga para cima, superfície firme e plana, lençol ajustado, berço sem travesseiros, brinquedos ou cobertas soltas; não sugerir inclinar colchão ou usar posicionadores.
- Ao representar cenas inadequadas para contrastar com a solução, evitar colocar efetivamente o bebê em risco. Mostrar objetos **em berço vazio**, removendo-os antes de mostrar o bebê.
- Manter acolhimento, não induzir culpa ou pânico em pais.

## Passo 4: Roteirização para retenção

**Padrão inicial para vídeos monetizáveis, sujeito às regras vigentes da plataforma:** duração total entre 65 e 85 segundos, com no mínimo 61 segundos de conteúdo útil, sem introduções ou enchimento. A duração sozinha **não assegura** qualificação ou receita.

### Ritmo dos atos (modelo para 75 s)
- **0–3 s: interrupção visual** com ação/contraste, texto curto e fala breve.
- **3–12 s: identificação e pergunta concreta.**
- **12–28 s: primeira explicação visual / revelação**, sem esconder a resposta só por suspense.
- **28–58 s: demonstração útil**, com 2–3 mudanças reais de ponto de vista.
- **58–70 s: resultado ou conclusão emocional e informativa.**
- **70–75 s: CTA breve**, opcional e contextual (“salve se isso pode ajudar na próxima madrugada”).

A organização dos atos pode variar. Priorizar **uma única ideia central** por episódio. Não espremer várias dicas sem conexão.

Regras práticas:
- 12–18 cenas por episódio de ~75 s, duração típica 3–7 s cada, com cortes motivados por ação/ideia, sem corte arbitrário a cada segundo.
- Personagens recorrentes e ambiente coerente dentro do mesmo episódio.
- Mudança de **estado visual** a cada 2–5 s: expressão, ação, câmera, texto animado, diagrama ou transição; não depender apenas de zoom lento em stills.
- Inserir pelo menos **duas sequências reais de motion design** que expliquem algo, não apenas enfeitem.
- Narração conversacional, frases pronunciáveis, 140–170 palavras/minuto como estimativa inicial; ajustar ao texto e voz reais.
- Não utilizar termos agressivos com mães, culpa, fake news ou exageros de risco.
- Criar final que feche a promessa do início.

## Passo 5: Direção de arte Foco Motion 3D

- Formato vertical **1080 x 1920**, 9:16, 30 fps.
- **Paleta-base:** azul-noite `#172C4A`, azul profundo `#254B75`, creme `#F6F0E7`, âmbar `#E9B66D`, verde-sálvia suave `#93ADA4`.
- Personagens 3D cinematográficos acolhedores, proporções naturais, textura de pele e tecidos, expressões claras sem caricatura excessiva.
- Ambientes familiares críveis, com consistência de figurino, hora do dia, cenário e iluminação.
- Começar **dentro da ação**, sem logo nos primeiros segundos.
- Transição-assinatura: **onda luminosa** que parte de um objeto da cena e se transforma em gráfico/explicação visual. Usar de modo funcional, no máximo 1–2 vezes por episódio.
- Motion design editorial premium: diagramas, infográficos, parallax real, composição em profundidade, tipografia cinética legível. Evitar brilho/partículas sem propósito.
- Reserva de texto: laterais com margem mínima de 10%, evitar controles e faixas superiores/inferiores da interface. Zona preferida aproximada: x 10–90%, y 18–75%. Não colocar palavras essenciais onde controles do TikTok cobrem o conteúdo.
- Legendas pt-BR exatas, no máximo 2 linhas por vez e apenas 1–2 palavras em destaque visual.
- Não repetir exatamente a mesma composição por mais de duas cenas seguidas.
- Não usar personagens visualmente idênticos às criações de uma franquia ou a pessoas reais sem autorização. Não imitar identidades visuais protegidas.

**Distribuição visual de referência, não rígida:** ~30% situação/emoção, ~40% explicação animada, ~20% demonstração e ~10% tipografia. Ajustar de acordo com assunto.

## Passo 6: Gerar o script técnico CENA A CENA

Cada cena precisa ter, obrigatoriamente:
1. `id`, `inicio_s`, `fim_s`, `duracao_s`, `ato`;
2. `objetivo_de_retencao`: por que a cena existe;
3. `narracao`: **somente o texto que será falado**, sem instruções de voz, tags ou cabeçalhos;
4. `texto_tela`: pequeno e literal, com acentuação correta;
5. `visual`: cenário, personagens, objetos, ações, continuidade e emoção;
6. `movimento_camera`: tipo, origem, destino, intensidade;
7. `motion_design`: objetos animados, lógica visual e transição;
8. `prompt_visual`: instrução pronta para criação/render de cena, sem incluir legenda gerada dentro da imagem;
9. `sfx_musica`: eventos sonoros e mixagem, sem competir com a voz;
10. `transicao`: corte/continuidade para cena seguinte;
11. `restricoes`: idades, sono seguro, anatomia, texto ou conteúdo médico relevantes.

**Narração TTS**: colocar perfil de voz fora de `narracao` e `tts_text`. Quando o áudio for gerado em Gemini, passar ao campo de texto de fala **apenas** as falas concatenadas; passar o perfil de voz somente em configuração/estilo quando a API permitir. Não enviar “PERFIL DE VOZ” como texto falado.

## Passo 7: Controle de qualidade antes de entregar

Verificar:
- [ ] O primeiro frame comunica uma situação/contraste e o primeiro segundo contém novidade visual.
- [ ] Promessa do gancho resolvida até o final, sem clickbait enganoso.
- [ ] Script original, sem reproduzir texto encontrado no Notion, em vídeos ou criadores.
- [ ] Voz total cabe nas durações; nenhum trecho requer fala ininteligível.
- [ ] Cenas contínuas, sem sobreposição nem buracos temporais.
- [ ] Ao menos duas transformações visuais explicativas claras.
- [ ] Mesmos personagens, roupas e objetos entre cenas conectadas.
- [ ] Ortografia pt-BR e legendas corretas, com margem de segurança.
- [ ] Recomendações infantis verificáveis e representações visualmente seguras.
- [ ] Cenários sem uso arriscado de berço, cama, coberta, medicamento ou alimentação.
- [ ] Conteúdo com mais de um minuto útil, sem loops artificiais para estender duração.
- [ ] Títulos/hashtags correspondem à busca identificada no print, sem spam.
- [ ] Não afirmar que o vídeo viralizará, receberá RPM maior ou será automaticamente elegível.

Quando falhar algum item crítico, corrigir o roteiro e os prompts antes de entregar. Se houver dúvidas médicas materiais, marcar `revisao_especializada_pendente: true` e não apresentar aquela orientação como definitiva.

## Formato de resposta obrigatório

1. **Leitura dos prints:** até cinco temas em ranking, com transcrição fiel de métricas visíveis e ressalvas.
2. **Escolha criativa:** assunto principal, série, busca exata, público/idade, premissa, 3 ganchos e gancho escolhido.
3. **Roteiro narrado completo:** texto de fala limpo e contínuo, fácil de copiar para TTS.
4. **Script de cenas:** tabela legível ou blocos sequenciais com os 11 campos definidos acima. Se for muito longo, apresentar síntese no chat e anexar documento completo.
5. **Pacote de publicação:** título pesquisável, legenda TikTok, 3–5 hashtags, CTA, capa sugerida, fonte/conteúdo a verificar.
6. **JSON de produção:** objeto válido no formato de `references/FORMATO_SAIDA.md`. Entregar como arquivo ou bloco JSON quando solicitado.
7. **Hipóteses de melhoria:** o que medir no TikTok Studio depois de publicar, especialmente retenção no 1º segundo, tempo médio, conclusão e visualizações qualificadas.

Para um exemplo, consultar `examples/ROTINA_REAL_75S.md`. Para estrutura do JSON e convenções técnicas, consultar `references/FORMATO_SAIDA.md`.

## Comandos do usuário que a Skill deve entender

- “Analise esses prints e escolha o assunto com maior potencial.”
- “Use o tema 3 e crie 15 cenas de 75 segundos.”
- “Só quero o JSON para edição.”
- “Gere a narração pronta para Gemini TTS.”
- “Reescreva mantendo a mesma quantidade de cenas, com mais Motion Design.”
- “Crie três aberturas diferentes para teste A/B/C.”

Não interromper o fluxo para perguntar o que já pode ser inferido dos prints; explicitar suposições sensíveis, principalmente faixa etária.
