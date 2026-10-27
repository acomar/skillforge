---
name: magnetic-video-director
description: "Dirige roteiros e edições de vídeos curtos ou longos a partir de narração, roteiro ou material bruto, combinando roteiro magnético, decupagem, J-cut, trilha, SFX, overlays, letterings e ritmo. Use para planejar, executar e auditar produção de vídeo dos canais Meu Bebê em Foco e Manga Oculto ou outros projetos."
metadata:
  category: content
  status: experimental
  version: "0.1.0"
---

# Magnetic Video Director

## Missão
Transformar uma ideia, roteiro, narração ou vídeo bruto em direção de vídeo executável, coerente, interessante e fiel à promessa editorial. É uma **skill de direção e orquestração**, não um renderer já implementado. Nunca declarar MP4 gerado, publicação realizada, integração n8n ativa ou retenção garantida sem evidência.

## Quando usar
- Planejar ou editar Shorts, Reels, TikToks e vídeos longos.
- Transformar roteiro + voz em storyboard, cenas, motion 2D, trilha e timeline.
- Auditar um vídeo em termos de ritmo, gancho, clareza e coerência visual.
- Trabalhar com material bruto (decupagem e J-cuts) ou 100% sintético (animação por cenas).

## Entrada
Aceitar pelo menos um: tema, roteiro, áudio, transcrição ou mídia bruta. Identificar público, canal, plataforma, duração, idioma, orientação, fontes, estilo e assets existentes. Se faltar um dado não essencial, usar defaults explícitos; perguntar somente bloqueios reais. Para Meu Bebê em Foco: pt-BR, tom acolhedor, linguagem simples, editorial 2D colorido, 9:16, foco em pais/cuidadores. Para Manga Oculto: espanhol latino, investigativo/cinematográfico, respeitar spoilers e direitos de uso. Não presumir permissão para publicar.

## Processo obrigatório
1. **Brief e verificação:** objetivo, promessa, público, evidências, licenças, riscos; separar fatos de hipóteses. Não transformar hipótese em fato.
2. **Narrativa magnética:** título e capa coerentes com primeiros segundos; teaser imediato e específico; introdução mínima; progressão por revelações; entregar promessa antes do CTA. Para vídeo longo, considerar teaser, introdução, conteúdo e CTA final; em Short, condensar e evitar vinheta longa.
3. **Mapa de beats:** cada beat tem intenção, informação nova, emoção, transição, narração e evidência. Evitar preenchimento artificial.
4. **Decupagem:** se há material bruto, escolher melhor tomada, remover erros, redundâncias e pausas inúteis, mas preservar respiração, naturalidade e sentido. Se é voz final, não cortar fonemas.
5. **Continuidade/J-cut:** antecipar áudio de um próximo plano apenas quando a inteligibilidade e a continuidade melhorarem; alinhar por waveform e validar lip-sync quando houver rosto falando. Não aplicar offset fixo universal.
6. **Direção visual:** criar storyboard e shot list; alternar enquadramentos com intenção; cut-out, parallax, pan, zoom in/out e transições por ação ou continuidade. Elementos visuais explicam o conteúdo, não só ilustram palavras. Para modo sintético, separar fundo/personagens/objetos/textos em camadas editáveis quando possível.
7. **Áudio e emoção:** trilha, SFX, ambiência e overlays com função narrativa. Ducking sob a fala, fades em mudanças emocionais, não sobrecarregar; verificar clipping e licenças.
8. **Letterings:** hierarquia, contraste, timing, safe areas; destacar conceitos-chave e não repetir todo o roteiro indiscriminadamente. Legendas acessíveis e sincronizadas, com opção palavra por palavra.
9. **Montagem:** exportar contrato de cena conforme references/SCENE-CONTRACT.md; escolher motor disponível (Remotion/FFmpeg/SVG/Lottie). Só executar render quando ferramentas, assets e runtime estiverem acessíveis. Gerar prévia antes de final.
10. **Crítica e revisão:** conferir alinhamento título/capa/abertura, entrega da promessa, precisão, continuidade, legibilidade, segurança, direitos, duração, áudio e frames problemáticos. Corrigir e registrar limites. Nunca afirmar métricas reais de retenção antes da publicação.

## Modos
- **material-bruto:** vídeo e/ou voz existente; decupagem e edição.
- **ai-generated:** voz + cenas 2D sintéticas e motion, sem exigir apresentador.
- **hybrid:** mídia real autorizada + gráficos + animações.
O modo é independente da plataforma e do canal.

## Entregáveis condicionais
- Sempre que possível: `brief.md`, `roteiro.md`, `storyboard.md`, `scene-plan.json`, `qa.md`.
- Com áudio e ferramentas: timeline, legendas SRT, projeto editável, `preview.mp4`.
- Apenas após render e QA: `final.mp4`. Publicação requer aprovação humana.
- Se não houver assets ou renderer: produzir plano de produção honesto, com pendências e placeholders explícitos.

## Regras de integração
- Preferir JS/TS, Remotion, FFmpeg, SVG e recursos gratuitos, sem presumir que estejam instalados.
- n8n pode orquestrar etapas via contrato JSON; credenciais e integrações são responsabilidade do ambiente.
- Reaproveitar skills especializadas já existentes no SkillForge (ex.: parental-motion-collage, manga-hq-video-editor-pt) em vez de duplicar seus renderers.
- Manter rastreabilidade da narração para cena e do conteúdo factual para fonte.
- Referências didáticas: references/LESSONS.md. As transcrições de origem são ASR não revisado e não descrevem integralmente a tela.
