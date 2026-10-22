# Runbook de execução no ChatGPT Work

## Primeiro uso
1. Carregar as nove skills em `skills/meu-bebe-*/SKILL.md` e orientar o agente pelo README desta pasta.
2. Com acesso autorizado, localizar a biblioteca `Meu Bebê em Foco > Kambam Blog` no Notion e os assets existentes no Drive. Separar referência popular de outlier mensurado.
3. Confirmar um **perfil de voz no Gemini** e uma **Bíblia visual autoral** a partir de amostras. Não deduzir preferências não documentadas.
4. Testar uma única sequência end-to-end: gerar imagem, animar no Grok, gerar áudio Gemini, compor overlay e exportar FFmpeg. Anotar limites reais de site, autenticação, créditos, duração e downloads.
5. Não solicitar senhas pelo chat. Fluxos de terceiros só quando houver integração/navegador disponíveis e autorização.

## Ordem de produção, por vídeo
1. Criar `production-state.json`, identificador, pasta de vídeo, custos e links de assets.
2. Pesquisa apresenta 3 ideias com fontes; o Produtor escolhe com base em demanda, diferenciação e viabilidade.
3. Embalagem formula até 3 pares título/thumbnail e define o gancho visual 0–30 s.
4. Roteiro entrega narração e mapa de retenção; Evidências corrige alegações sensíveis.
5. Arte entrega Bíblia visual, fichas dos personagens, storyboard (~40 unidades narrativas, não ~40 chamadas ao Grok), começo/fim de cada plano, overlays e transições.
6. Áudio prepara locução e desenho sonoro. Fazer **animatic** usando stills, áudio provisório, movimentos de câmera simulados e duração real.
7. Revisar animatic antes de comprometer créditos: ritmo, continuidade, complexidade de arte, micro-revelações e valor mesmo sem som.
8. Gerar/animar assets; classificar **aprovado / aproveitável / rejeitado**. Refazer somente se o resultado final realmente perde qualidade, clareza ou confiança; usar cortes, máscaras, congelamentos e composição como alternativas.
9. Montar timeline em 16:9, motion integrado na própria cena, gráficos legíveis e sincronização de locução. Não cortar de estética premium para slide genérico.
10. Fazer revisão de vídeo sem som, depois áudio isolado e depois audiovisual integrado. Conferir arte, ciência, licenças e erros técnicos.
11. Preparar pacote para aprovação do criador; publicação somente após autorização ou política explícita de autonomia.
12. Registrar analytics, receita, custos e hipóteses de melhoria após publicação.

## Formatos mínimos
- `research-brief.md`, `packaging.md`, `roteiro-validado.md`, `fact-check.md`
- `visual-bible.md`, `storyboard.md`, `animatic.mp4` quando renderizado
- `image-manifest.csv`, `animation-manifest.csv`, `voice-bible.md`, `tts-manifest.csv`
- `timeline.md`, `qc-report.md`, `performance-report.md`, `production-state.json`

Status: **planejado / em_execucao / bloqueado / validado**, com artefatos verificáveis. Nunca indicar que um render, login, upload, download ou publicação ocorreu se não ocorreu.

## Critérios de decisão
- Segurança/veracidade e direitos de uso vêm primeiro.
- Qualidade percebida, coerência de cena, narrativa e legibilidade vêm antes de economia marginal.
- Gastos adicionais precisam de finalidade e hipótese de benefício; não há limite numérico fixo.
- Meta de 100% de retenção é aspiracional; resultado <70% gera investigação, não comprova falha isolada.
- Se uma integração falhar, registrar erro e oferecer plano de contingência; não exigir transferência manual por padrão.
