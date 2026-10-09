# Mapa da referência para a montagem

## Contrato de fidelidade

Use o pedido para identificar o que deve permanecer equivalente: sequência, duração de planos, enquadramento, movimento, texto, transições, falas ou arco de música. Na ausência de contrato específico, preserve a macroestrutura e os beats importantes, registrando aproximações. Não prometa equivalência pixel a pixel com material diferente.

Se o objetivo é somente duplicar um arquivo fornecido, faça a operação de arquivo adequada; não reencode nem recrie uma montagem inteira sem necessidade.

Uma linha por beat relevante:

| ID | Referência | Saída | Fonte/trecho | Imagem e movimento | Fala/som/texto | Transição | Diferença e revisão |
| --- | --- | --- | --- | --- | --- | --- | --- |
| beat-001 | 00:00–00:12 | 00:00–00:12 | source-a, 00:34–00:46 | abertura em plano geral | fala original e título fornecido | corte | conferir leitura do título |

Este exemplo ilustra o formato; não é uma observação de um vídeo real. IDs permanecem estáveis ao ajustar tempos.

## Três relógios

`reference_range` aponta para a montagem estudada; `source_range` é o trecho do arquivo usado; `output_range` é a posição na entrega. Para playback normal, duração de fonte e duração de saída coincidem. Com velocidade `r`, duração de saída = duração de fonte / `r`; a extensão de uma still é uma decisão de saída sem tempo de fonte equivalente.

Use intervalos semiabertos `[in, out)` para evitar frames duplicados entre clips. FPS do projeto deve ter representação racional, por exemplo `30000/1001`. Quantize decisões ao grid de frames da saída; não arredonde todos os tempos de origem antes de selecionar. Fonte com FPS variável usa timestamps reais; não reconstrua seu tempo multiplicando número de frame pelo FPS médio.

Valide antes do render:

- Todos os arquivos e streams referenciados existem.
- Intervalos são crescentes e ficam dentro da fonte.
- Duração pretendida inclui sobreposição das transições, não só soma bruta dos clips.
- Lacunas, holds, silêncio e overlaps são intencionais.
- Legendas e overlays terminam conforme a decisão editorial.
- Cada beat da faixa solicitada foi mapeado ou consta como pendência.

O modelo `assets/edit-plan.example.json` guarda essas decisões. Não é um executor nem um esquema completo de todos os filtros/editores; gere comandos ou um projeto específico ao motor selecionado, mantendo a relação com o plano.

## B-roll, personagens e gráficos

Registre fonte, origem, autorização conhecida e função para cada material externo. Não substitua algo específico por imagens genéricas sem declarar a mudança. Em histórias/HQ, acompanhe aparência dos personagens, cenário, direção do movimento e continuidade entre imagens. Em aulas/demos, mantenha texto legível e telas coerentes com a fala.

Detalhes tipográficos só podem ser tratados como exatos quando medidos ou fornecidos. Indique fonte aproximada se ela não foi identificada. Gráficos complexos podem exigir SVG/React/Remotion; simples títulos podem ser feitos no motor já escolhido.
