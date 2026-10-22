# Meu Bebê em Foco AI Studio

Estúdio editorial para vídeos **longos originais de 10–12 minutos em português brasileiro**, voltados especialmente a famílias de crianças de 1–4 anos, com flexibilidade para outros temas de parentalidade. Meta de negócio: produzir aproximadamente um vídeo de qualidade por dia, desenvolver um canal economicamente sustentável e crescer rumo a 100 mil inscritos. Nenhuma métrica de viralização ou retenção é garantida.

**Oito skills especialistas + um Produtor Executivo**. As skills ficam em `skills/` na raiz, em respeito ao padrão SkillForge; esta pasta reúne o agente, o fluxo de produção e modelos de operação. Não confundir com a skill existente `foco-motion-tiktok`, que é para vídeos curtos verticais.

## Agente e skills
- [Produtor Executivo](../skills/meu-bebe-produtor-executivo/SKILL.md): orquestração, estado e portões.
- [Estratégia e Pesquisa](../skills/meu-bebe-estrategia-pesquisa/SKILL.md): temas, biblioteca Notion, outliers.
- [Embalagem e Crescimento](../skills/meu-bebe-embalagem-crescimento/SKILL.md): título, thumbnail, abertura e conversão.
- [Roteiro e Retenção](../skills/meu-bebe-roteiro-retencao/SKILL.md): narrativa original e progressão.
- [Evidências e Segurança](../skills/meu-bebe-evidencias/SKILL.md): checagem científica e responsabilidade.
- [Arte e Imagem](../skills/meu-bebe-arte-imagem/SKILL.md): Bíblia visual, storyboard, imagens e continuidade.
- [Áudio e Narração](../skills/meu-bebe-audio/SKILL.md): Gemini, música, efeitos, mix.
- [Vídeo e Montagem](../skills/meu-bebe-video-montagem/SKILL.md): Grok/Flow, overlays, FFmpeg e revisão final.
- [Performance e Rentabilidade](../skills/meu-bebe-performance-rentabilidade/SKILL.md): resultados e retorno econômico.

## Decisões criativas obrigatórias
1. Vídeo deve ser interessante **mesmo sem som**. Narração aprofunda o entendimento, não substitui a linguagem visual.
2. **Continuidade cinematográfica**: uma cena explica a próxima. Evitar corte de animação premium para gráfico visualmente pobre.
3. Preferir **overlays na própria imagem**: pausar quadro, usar máscaras e profundidade, animar símbolos e palavras sobre a cena, depois retomar o movimento.
4. Estilo autoral: narrativas ilustradas expressivas em 2D, motion design premium, 3D estilizado quando serve à história; referência aos princípios narrativos do BibleProject, sem copiar sua estética/propriedade intelectual.
5. **Animatic obrigatório** antes da geração definitiva de clipes caros. Uma sequência de imagens e áudio provisório deve validar ritmo e transições.
6. Nenhum teto arbitrário de gerações. Não refazer apenas por perfeccionismo: decidir pelo valor perceptível e retorno esperado. A primeira tomada aproveitável pode ser retrabalhada, mas não rebaixar qualidade para poupar crédito.
7. Revisão em três perspectivas: **sem som**, **som sem imagem**, **completa**.
8. Pesquisa e checagem de afirmações sobre infância obrigatórias; conteúdo educativo original, sem diagnósticos individualizados.
9. Aprovação do criador antes de publicar, salvo autonomia explícita posterior.
10. Reter metadados de custos e resultados; aprender com publicação real sem declarar sucesso fictício.

## Materiais
- [RUNBOOK-WORK.md](RUNBOOK-WORK.md) para executar no ChatGPT Work e testar integrações.
- [brief de produção](templates/brief-producao.md).
- [plano de cenas](templates/plano-cenas.csv).
- [estado da produção](production-state.example.json).

**Maturidade:** especificação experimental. Este repositório documenta habilidades e procedimento; não prova que o Work consiga autenticar, navegar Grok/Gemini, transferir arquivos ou renderizar automaticamente em todos os ambientes. Essas integrações precisam de teste ponta a ponta.
