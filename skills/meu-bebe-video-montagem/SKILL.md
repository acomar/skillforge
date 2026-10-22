---
name: meu-bebe-video-montagem
description: "Planeja animações Grok/Flow, cria overlays integrados, animatic e edição FFmpeg para longos premium do Meu Bebê em Foco. Use após storyboard e narração, antes do controle de qualidade."
metadata:
  category: content
  status: experimental
  version: "0.2.0"
---

# Diretor de Vídeo e Montagem

## Regra central: continuidade cinematográfica integrada
Motion graphics não são intervalos visuais separados: fazem parte da **mesma cena**, mantendo personagens, enquadramento, luz, profundidade, textura e linguagem do vídeo original. Prefira overlay, máscara e profundidade em vez de corte para gráfico genérico.

## Procedimento
1. Interpretar storyboard e Bíblia visual; registrar mapa de continuidade entre planos, quadro de entrada/saída, posição dos personagens, figurino, luz e eixo de câmera.
2. Antes de gastar crédito em animação, montar **animatic com stills, áudio provisório, freeze frames, corte e movimentos simulados**. Avaliar cena a cena com Arte e Roteiro.
3. Animar cenas prioritárias em Grok/Flow apenas **onde a ferramenta realmente estiver disponível**. Não inferir limites da interface; guardar prompts, gerações, qualidade e custos reais.
4. Para explicações, aplicar **freeze → overlay sobre frame original → continuidade/retomada**. Composição de camadas pode usar FFmpeg, HTML/CSS/JS renderizado, Remotion ou ferramentas validadas; HyperFrames/Motion apenas se compatíveis e acessíveis.
5. Triagem: `aprovada`, `aproveitável` com corte, correção/mascaramento, ou `rejeitada` se deformação grave, incoerência, queda visual perceptível ou risco. Não repetir gerações por hábito e não aceitar cenas fracas só para poupar créditos. **Não há limite rígido de chamadas**.
6. Montagem 16:9 com sincronização de locução, legendas legíveis, sfx, música, transições funcionais, pausa intencional e acabamento uniforme. Não exigir movimento intenso em cada segundo.
7. **Três passes de QA obrigatórios**: (a) sem som, a história visual funciona? (b) somente áudio, a narrativa se sustenta? (c) integral, áudio e visual se ampliam em vez de se atrapalhar?
8. Inspecionar erros anatômicos, artefatos, clipping de áudio, black frames, quebra de continuidade, links, direito autoral, ciência visual, legendas e promessas da thumbnail.

## Critérios de bloqueio
Plano que compromete entendimento, coerência, segurança, copyright ou qualidade percebida deve ser corrigido. Adaptar edição ao material aproveitável, mas sem perda perceptível.

**Saídas:** `animatic.mp4` quando gerado, `animation-manifest.csv`, `timeline.md`, `qc-report.md`, vídeo final somente após exportação e conferência real.
