# Contrato de edição de Shorts com Remotion

## Arquitetura
A narração/roteiro determina a duração real do conteúdo. A composição é uma sucessão de shots, cada um com fundo, layers e movimento. O renderer usa uma timeline determinística de frames. Trabalhe com assets **locais e autorizados**. Não use URLs de terceiros diretamente no projeto.

O starter encontra-se em `renderer/`. É um compositor mínimo original, não uma cópia dos três projetos de referência; ele renderiza PNGs locais em camadas, formas, textos, entradas escalonadas, zoom/câmera leve e áudio local quando fornecido. Ainda não possui geração automática de imagens, recorte por IA, detecção de fala, legendas palavra a palavra ou sincronização labial. Para voz e legenda sincronizadas, produza essas mídias em etapa externa e adapte a timeline a partir do tempo real do áudio.

## Como criar o JSON
Em `renderer/public/project.json`, use:
```json
{
  "title": "Seu título",
  "editorialStatus": "approved_for_render",
  "audio": { "voice": "media/voice.mp3", "music": "media/music.mp3" },
  "shots": [
    {
      "id": "s01",
      "durationFrames": 120,
      "background": "#57B8FF",
      "caption": "Texto conferido do trecho de voz.",
      "camera": {"zoomFrom": 1, "zoomTo": 1.04, "panX": 8, "panY": -5},
      "layers": [
        {"id":"paper","kind":"shape","x":540,"y":700,"w":690,"h":450,"color":"#FFD761","enter":"pop","startFrame":0},
        {"id":"headline","kind":"text","text":"O QUE LEVAR?","x":540,"y":570,"w":650,"h":180,"fontSize":86,"color":"#243047","enter":"rise","startFrame":6},
        {"id":"photo","kind":"image","src":"media/recorte.png","x":540,"y":1050,"w":560,"h":600,"enter":"slide-left","startFrame":15,"rotate":-4}
      ]
    }
  ]
}
```
Os valores `x,y` são o **centro** da camada, em pixels. `w,h` são largura e altura. `durationFrames` usa fps 30. `enter`: pop | rise | slide-left | slide-right | fade. `startFrame`: frame relativo ao shot, não ao vídeo. `rotate` em graus. Textos podem ser `text` ou `tag`; imagens PNG/JPG locais são `image`; `shape` para cartões abstratos.

Campos `audio` são opcionais: sem arquivo, vídeo de exemplo será **silencioso**. As músicas devem ser licenciadas e não exigem vocal. Arquivos devem estar dentro de `renderer/public/media/`.

## Fluxo recomendado
1. Criar roteiro e timeline alinhada a áudio real.
2. Separar cada cena em 2–6 camadas independentes. Elaborar artes sem palavras impressas no bitmap.
3. Importar fotos de acervo/licença, PNGs com transparência e ícones próprios.
4. Registrar cada camada no JSON; alterar a câmera uma vez por shot.
5. Rodar `npm install`, `npm run validate` e `npm run preview`.
6. Renderizar `npm run render`, inspecionar frames em início/meio/fim das cenas e usar `ffprobe` no MP4.
7. Se houver TTS e áudio, ajustar cada shot aos tempos reais e revisar legendas antes do arquivo final.
8. Salvar checklist editorial e gerar pacote de metadados para as duas plataformas, sem publicar automaticamente.

## Critérios de bloqueio
`editorialStatus` diferente de `approved_for_render` bloqueia renderização pelo comando de validação. Isso NÃO substitui revisão humana real: o campo só pode ser alterado após análise dos riscos e fontes. O exemplo é ficcional/educativo e contém textos ilustrativos, não é um vídeo final para postagem.

## Ritmo de Shorts
- Gancho visível no frame 0; texto principal entre x=100..930, aproximadamente y=320..1450.
- Mudanças de foco úteis a cada 2–5s, com cenas entre 2–6s sempre que coerente.
- Fotografia não pode ser falsa evidência documental. Ilustrações e renders devem ser sinalizados quando a distinção for relevante.
- Legendas ocupam área segura e não podem interferir com botões das interfaces; verificar no aplicativo.
- Publicar somente após aprovação humana e revisão de áudio/licenças.
