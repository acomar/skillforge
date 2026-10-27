# Contrato de cena v0.1

Um projeto possui `projectId`, `channel`, `language`, `aspectRatio`, `fps`, `mode`, `assets` e `scenes`. Cada cena exige `id`, `startMs`, `durationMs`, `narration`, `intent`, `visual`, `camera`, `audio`, `transition` e `evidence`.

Exemplo ilustrativo (não significa que arquivos ou áudio existam):
```json
{
  "projectId": "demo-sono",
  "channel": "meu-bebe-em-foco",
  "language": "pt-BR",
  "aspectRatio": "9:16",
  "fps": 30,
  "mode": "ai-generated",
  "assets": [],
  "scenes": [
    {
      "id": "s01",
      "startMs": 0,
      "durationMs": 3200,
      "narration": {"text": "Seu bebê acorda várias vezes à noite?", "audioAssetId": null, "inMs": 0, "outMs": 3200},
      "intent": "gancho e identificação",
      "visual": {"background": "quarto-noturno", "layers": ["berco", "bebe"], "letterings": []},
      "camera": {"type": "zoom-in", "fromScale": 1, "toScale": 1.08, "easing": "ease-in-out"},
      "audio": {"musicAssetId": null, "sfx": [], "ducking": true},
      "transition": {"type": "cut", "jCutMs": 0},
      "evidence": {"sourceIds": [], "status": "editorial"}
    }
  ]
}
```

## Validações
- `startMs >= 0`, `durationMs > 0`; sem sobreposição não intencional.
- Narração alinhada a duração real do áudio, nunca só estimada por texto.
- J-cut positivo só com material de áudio compatível; documentar offset.
- Referências a assets devem existir ou ser declaradas placeholders.
- Elementos de texto respeitam safe areas e contraste.
- A saída é um contrato para um motor de render, não o motor em si.
