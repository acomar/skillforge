---
name: meu-bebe-audio
description: "Prepara narração Gemini em pt-BR, direção emocional de voz, música, efeitos, tempos e revisão de mix. Use ao produzir áudio de longos após roteiro validado."
metadata:
  category: content
  status: experimental
  version: "0.2.0"
---

# Diretor de Áudio e Narração

## Entradas
`roteiro-validado.md`, transições planejadas, perfil de voz escolhido pelo criador, emoções por cena, acessos autorizados.

## Processo
1. Criar `voice-bible.md`: voz escolhida e confirmada, pt-BR, timbre, ritmo, pronúncia, pausas e variação emocional adequada, sem voz caricata.
2. Dividir texto em trechos com continuidade perceptível; formatar prompts de geração no Gemini e registrar modelo, parâmetros, limites, versões e nomes de arquivos efetivamente produzidos.
3. Quando ambiente autorizar e suportar, gerar áudio e baixar via integração/navegador; **não presumir** acesso a Gemini, exportação ou controle automatizado.
4. Revisar pronúncia, velocidade, trechos cortados, consistência de timbre, silêncios e respirações. A fala deve completar e não repetir literalmente o que o visual já conta.
5. Produzir guia de música e efeitos com licença verificada. Mix sem cobrir a voz; efeitos motivados por gestos, overlays e revelações.
6. Sincronizar pistas com congelamentos e retomadas do vídeo; entregar áudio provisório para animatic **antes** do render final.

## Aceite
Teste de **som sem imagem**: compreensão, emoção, pausas, ritmo, volume, ausência de erros. Reutilizar voz aprovada nos próximos vídeos, respeitando disponibilidade e permissões.

**Saídas:** `voice-bible.md`, `tts-manifest.csv`, `audio-cues.md`, stems/locuções somente se gerados e inspecionados de fato.
