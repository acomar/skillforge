# Produção e sincronização

## Ambiente e dependências reais

Rode `scripts/popup_tools.py doctor`. A opção `--library CAMINHO` informa um clone específico. O diagnóstico procura também `LEMO_OPUSCAR_HOME`, a biblioteca da skill Lemo instalada e `~/lemo-opuscar`. Um relatório sem faltas ainda exige teste de um quadro com WebGL e carregamento de fontes.

A biblioteca pode estar dentro da skill Lemo instalada, em `lemo-opuscar/library`, ou no diretório apontado por `LEMO_OPUSCAR_HOME`. Resolva o caminho no ambiente atual. O projeto do filme histórico não está disponível; seu código, áudio, índices e SFX não acompanham esta skill.

Leia a skill `lemo-opuscar`, seu adaptador Windows e as instruções da biblioteca antes de produzir. Use o `styles/paper-popup/STYLE.md` como base técnica, com as adaptações desta skill para cor, personagens, som, FPS e legendas. Leia `core/README.md` para os comandos instalados. A entrada HyperFrames, quando obrigatória no ambiente, não significa que os arquivos antigos já tenham sido convertidos.

Não instale renderizadores durante uma tarefa que só pede criar/editar esta skill. Numa produção, prepare as dependências necessárias usando o adaptador da skill Lemo, após conferir o que já existe. Não editar `core/`, não construir o filme dentro de `styles/`, não atualizar um clone funcional sem necessidade.

Em Windows, use `.venv/Scripts/python.exe`, não suponha `.venv/bin/python`. Não precisa de WSL. Use argumentos de processo adequados para caminhos com espaços. Inspecione `setup.ps1`, `setup.sh` e o ambiente em vez de executar receitas com o nome de usuário antigo. Se for usar Git Bash com ferramentas POSIX, confira conversão de caminhos MSYS; `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8` e `MSYS_NO_PATHCONV=1` resolveram problemas do ambiente antigo, mas não são prova de necessidade no atual.

O demo de `paper-popup` pode não estar no sparse checkout. O adaptador Windows consultado só oferece `library`, `status`, `deps`, não um modo `demo`. Após escrever o tratamento, obtenha o demo usando o método documentado pela versão instalada ou o Git sparse-checkout nativo com um argumento literal para o caminho. Use a técnica do demo, com sua licença MIT, preservando atribuições no código redistribuído; crie a narrativa, poses, cenários e tempos do roteiro atual.

## Projeto e roteiro

Estrutura funcional sugerida, ajustável ao projeto:

```text
projeto/
  inputs/                  roteiro e arquivos recebidos, preservados
  assets/                  voz, fontes, SFX, poses e words_script.json
  work/                    estado, intermediários, quadros, medições
  outputs/                 MP4, poster, SRT e relatório final
  index.html               entrada do motor
  story.js                 timeline única e referências aos beats
  pages.js                 cenários e pisos
  art.js / art_chars.js    objetos, cartões e poses
  sets.js                  peças e mecanismos
  main.js                  câmera, luz, livro e estados dos atores
  hud.js                   legendas e avisos
  TREATMENT.md
  storyboard.json
  build.ps1                ou outro comando reproduzível adequado ao sistema
  CREDITS
```

Não criar módulos vazios apenas para completar a árvore. É possível consolidar arquivos se preservar responsabilidades e clareza.

Transforme o texto em beats semânticos. Cada beat registra: `id`, trecho literal da narração, âncora de palavra, cenário, ação visível, personagens/idade, mecanismo explicativo, rótulos, paleta, transição e fonte das afirmações que exigirem verificação. Resolva a cena pelo que é explicado: uma comparação pede contraste visível, uma sequência pede mecanismo em etapas, um afeto pede gesto/expressão.

Um roteiro novo não herda as alegações de saúde do filme antigo. Para afirmações de saúde/desenvolvimento, consulte fontes oficiais atuais e o Second Brain. Registre suporte e limites; uma suspeita de erro no roteiro recebido exige apontamento antes de narrar a afirmação como fato. Cenas de cuidados também precisam ser coerentes com a orientação verificada. A bibliografia técnica da skill não valida conteúdo clínico.

## Narração, alinhamento e página

1. Preserve o áudio fornecido. Se não existir, obtenha-o pelo fluxo já configurado ou esclareça o acesso faltante; não presumir que a existência de uma assinatura concede API.
2. Meça duração, silêncio inicial, cortes e correspondência ao roteiro. Faça alinhamento/transcrição com ferramenta real, revisando palavras, nomes e pausas. Estimativas são aceitáveis no planejamento, não no SRT final.
3. Normalize o alinhamento para lista `{text, start, end}`, em segundos relativos à voz, uma palavra por item. Tempos ordenados, positivos, sem sobreposição e dentro do áudio. Não empilhar novamente offsets que já foram aplicados.
4. Defina `LEAD` (início da voz no filme, 1,0 s como ponto de partida), `NARR` (duração medida da voz) e `DUR` (inclui lead e final com sustentação suficiente). Tempo de palavra no filme = `LEAD + start`. O helper gera cues já nessa base; não somar o lead outra vez no HUD.
5. Ache a primeira e a última palavra de cada beat pelo texto e pelo alinhamento atual. Quando uma expressão se repete, identifique a ocorrência correta. Nunca reutilize índices, `SPREAD_W`, `TURNS`, `scene_bounds.json` ou lista `KEY` de outro roteiro.
6. A virada pode começar 0,55 s antes da âncora do beat seguinte e terminar 1,15 s depois, conforme o exemplo. Ajuste a sobreposição se apagar a fala anterior ou prejudicar a próxima cena. A permanência de cada cartão depende do próprio texto e da leitura, não só da dobra da página.
7. Gere SRT e cues de HUD pelo helper. Escolha palavras-chave pelo significado do roteiro e use amarelo da marca. Não realçar palavras demais.

## Render determinístico

O motor Lemo usa HTTP, módulos ES, three.js r170 e arte Canvas2D. A página expõe `window.READY`, `window.render(t)`, `window.DUR`; `window.EV` é opcional para eventos de SFX. Aguarde fontes e imagens antes de `READY`. Para inspeção de rótulos pelo motor, implemente `window.TEXTS(t)` com caixas e texto completo.

Qualquer tempo, pose, partícula ou câmera deve poder ser reconstruído por `t`, inclusive ao voltar no tempo e em workers separados. Nada de acumular estado por frame, relógio de parede ou aleatoriedade sem semente. Evite redesenhar canvases caros quando a pose não mudou.

O palco usa medidas físicas próximas ao livro de 44×30 cm. Cartões com frente, verso e alpha; sombras respeitam o recorte. Mantenha a luz externa quente na cena noturna; noite é também uma mudança da arte do papel. Use tone mapping neutro para não desviar as cores pastel. Confira câmera, foco e profundidade de campo na escala macro. Virar personagem com desenho espelhado/troca de pose evita expor um cartão de lado.

Execute a partir de `LIB`, com o caminho absoluto do projeto como argumento:

```text
node core/render/still.mjs PROJETO 1.5 --size 1080x1920 --out PASTA_DE_QUADROS
node core/render/events.mjs PROJETO --size 1080x1920
node core/render/video.mjs PROJETO --fps 30 --workers 3 --size 1080x1920 --out VIDEO_SEM_AUDIO
```

São formas dos comandos consultados, não uma promessa de tempo de render ou de GPU específica. Verifique opções na instalação atual. Comece com quadros representativos, depois uma sequência curta com virada e voz, e só então renderize tudo. Se houver falha, investigue o erro antes de repetir.

## Voz e efeitos

O áudio padrão contém só voz e SFX reais do usuário. Procure primeiro os SFX recebidos com o projeto e depois a biblioteca de efeitos configurada pelo usuário, quando acessível. A seleção já documentada pela skill `bebe-ensaio-visual` pode ajudar, se existir no ambiente. Sem os arquivos, registre a falta; os nomes `sfx_03`, `04`, `08`, `10`, `12`, `13`, `15` do resumo não identificam arquivos universais.

Uma virada admite um whoosh baixo; `hang`, `flip` e pequenas revelações podem admitir um click. Referência inicial do exemplo: whoosh 0,55; click 0,22; intervalo mínimo de 1,4 s entre clicks. Esses são ganhos lineares iniciais, dependentes do nível do arquivo. Confira picos, sensação e competição com a voz. Não herdar 26 clicks como meta, nem disparar som para toda peça, sílaba ou letra.

Os offsets de pico `PK` pertenciam àqueles sete arquivos. Em novos arquivos, meça/escute o transiente e alinhe o pico ao gesto. Comece de `t_evento - offset_do_pico`; ajuste perceptivamente. Não alinhe apenas o começo do arquivo nem copie o avanço de 0,25 s sem verificar o som.

Trate a voz apenas quando necessário (ponto de partida: passa-altas perto de 90 Hz e compressão leve). Exporte mix com headroom e normalize para cerca de −14 LUFS integrados, pico verdadeiro máximo −1,2 dBTP, sem distorção. Não reduzir tudo duas vezes por aplicar limitador e normalização sem medir.

Use `core/render/mux.sh` somente se houver shell POSIX adequado e após inspecioná-lo; caso contrário, traduza o mux para FFmpeg no comando de build do Windows, com normalização em duas passagens e BT.709 coerente. Não repetir o caminho POSIX antigo por conveniência. O build deve reconstruir voz/SFX, vídeo e mux com entradas locais e registrar versões/licenças necessárias.
