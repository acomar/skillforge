# Identidade e linguagem do livro pop-up

## Cores, materiais e marca

`../assets/brand-tokens.json` concentra os valores. As cinco cores vêm da identidade oficial v1 e são aproximadas; a prancha aprovada prevalece na percepção. Papel marfim, tinta castanha e azul de noite são apoios de produção definidos nesta adaptação, não novas cores oficiais.

Use base de papel clara, iluminação quente e sombras suaves. A mesa e os objetos reais ficam naturais e pouco saturados, com o livro em destaque. Evite neon, preto puro dominante, contornos agressivos e estética assustadora. Mantenha contraste nos textos: rosa, amarelo, verde e lavanda claros pedem tinta escura; texto creme/amarelo nas legendas precisa de contorno castanho.

Cada página usa uma família dominante e um ou dois acentos. Sugestões de associação, sem obrigação narrativa:

| Função da cena | Dominante | Acento |
| --- | --- | --- |
| Acolhimento e vínculo | Rosa | Amarelo |
| Explicação e rotina | Azul | Verde |
| Sono e calma | Cinza-lavanda | Azul |
| Noite | Azul de noite derivado | Amarelo suave |
| Descoberta e brincadeira | Verde | Amarelo |
| Síntese | Papel marfim | Azul e rosa |

Não force todas as cores em todas as cenas. Não use rosa/azul para limitar ações por gênero. Não invente um logo nem recorte automaticamente o logo da prancha; quando necessário, componha o nome do canal ou use o arquivo de marca fornecido.

## Família e representação em papel

Veja `../assets/family-board.png`. Não use o painel inteiro, os textos ou as expressões recortadas da prancha como substituto de arte de cena. Ela orienta o desenho original.

| Personagem | Traços e roupa base |
| --- | --- |
| Lucas | Adulto ~32, pele clara, cabelo castanho-escuro curto e volumoso, barba curta, olhos castanhos, camiseta azul e calça neutra. |
| Juliana | Adulta ~30, pele clara, cabelo castanho longo e ondulado, olhos castanhos, blusa rosa e calça neutra. |
| Sofia | 4 anos, pele clara, cabelo castanho longo/ondulado, laço rosa, vestido lilás e proporções infantis. |
| Enzo | 6 meses, pele clara, pouco cabelo castanho claro e topete discreto, olhos castanhos, bochechas arredondadas, body amarelo-claro. |

Traduza rosto, cabelo, roupa e afeto para ilustração de recorte: contorno castanho arredondado, borda marfim, espessura discreta de cartão e poses legíveis. O palco é tridimensional; o personagem continua uma peça plana. Não aplicar os materiais volumétricos da prancha ao corpo inteiro por confundir identidade com formato.

Preserve rosto, idade aparente, proporções e roupa dentro da sequência. Nomeie as poses e registre a referência usada. Piscar, sorriso, direção do olhar e braços mudam por estado/pose; não redesenhar uma pessoa diferente em cada quadro.

Para um roteiro sobre bebê de 2 meses, o padrão é bebê didático anônimo de 2 meses com a paleta da marca. Enzo permanece o personagem canônico de 6 meses. Quando o roteiro não exige a família, use objetos, mecanismos ou personagens adequados ao conteúdo sem inserir os quatro por rotina.

## Gramática de papel

- Livro de capa dura aberto numa mesa. Textura de papel sutil, bordas e sombra de recorte com alpha; cartões não projetam sombras retangulares.
- Peças `pop` erguem-se pela base, de trás para frente; peças `wall` ficam no cenário; peças `hang` descem em fios. Mecanismos `flip`, ripas, abas e fitas explicam uma mudança concreta.
- Cenários domésticos preferenciais: quarto, sala, cozinha, brincadeiras e banheiro. Escolha o cenário necessário ao trecho; não reproduza a sequência de cômodos do exemplo.
- Papel se move por dobra, giro de aba, deslize, balanço ou troca de pose. Evite deformação gelatinosa. Câmera macro suave; aproximação tem função narrativa.
- Virada de página troca o assunto e a cor. Não esconda um rótulo antes da fala correspondente terminar. Preserve leitura durante a transição, antecipando ou atrasando o mecanismo conforme a fala.
- Um gesto afetivo funciona como encerramento se ele fizer parte da mensagem. Evite confete em toda dica e movimento contínuo sem informação.

## Vertical e textos

Os valores de `layout_px` são o ponto de partida conservador para TikTok/Reels, não uma garantia sobre qualquer interface de aplicativo. A figura principal deve ocupar o centro sem grandes vazios, com margem para mãos, coração, fios e legendas.

Em 1080×1920: coluna útil x=120–900; conteúdo importante a partir de y=270; zona inferior a partir de y=1440 livre de informação essencial. Arte principal em y=300–1230; legenda com baseline em y=1400, largura até 760 e centro x=510. Aviso informativo, quando pertinente, no final com baseline y=1300, acima da legenda. A posição antiga y=1560 do resumo cruza a interface e foi substituída.

Essas reservas valem na imagem projetada pela câmera, não apenas nas coordenadas do mundo. Confira todos os enquadramentos e viradas. Como ponto de partida do livro de 44×30 cm, use coluna de ±8 cm; uma peça de mais de 16 cm precisa ser redimensionada ou demonstrada como visível no quadro. Não usar isso como limite universal para objetos de fundo.

Cartões de leitura: títulos curtos, listas empilhadas, pares ou grade 2×2; nunca texto longo numa faixa horizontal. Separe o que o narrador diz do que precisa ser lido. Ajuste o tempo de permanência à leitura real.

Legenda: Fredoka 700, 84 px de base, 98 px na palavra-chave, uma linha e até duas palavras; reduza o tamanho quando necessário para caber sem quebrar. Fonte e tamanhos são escolhas deste formato. Carregue os glifos portugueses antes de `READY`. Palavra atual faz um pulso curto; a futura pode ficar a 50% apenas quando continuar legível. Não antecipar palavras além do grupo atual, nem manter texto em silêncios longos.
