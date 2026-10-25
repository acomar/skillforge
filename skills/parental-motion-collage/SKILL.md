---
name: parental-motion-collage
description: "Produz e edita Shorts verticais de parentalidade em colagem editorial 2D colorida: apura assunto, cria roteiro por beats, separa camadas, anima com Remotion, integra voz/música/legendas, renderiza MP4 e audita. Use para Shorts educativos, explicadores, notícias e mitos sobre gestação, bebês, infância e rotina familiar, especialmente no Meu Bebê em Foco."
metadata:
  category: content
  status: experimental
  version: "0.1.0"
---

# Parental Motion Collage

## Missão e escopo
Criar **exclusivamente Shorts verticais 9:16**, para YouTube Shorts e TikTok, com edição dinâmica e afetiva: fotografias recortadas, papel colorido, infográficos, tipografia cinética, animação por camadas e efeitos leves. Uma edição de vídeo para as duas redes, mudando apenas título, descrição, hashtags e capa quando necessário.

Este é um **fluxo executável por agente**, acompanhado de um **renderer Remotion inicial** nesta pasta. Não é uma integração automática com geração de imagem, TTS, notícias ou postagem. Não declare que produziu MP4 sem renderizar e inspecionar o arquivo. A publicação exige aprovação humana.

## Quando usar
- "Crie/edite um Short em colagem colorida para Meu Bebê em Foco", "explique essa notícia para pais", "motion collage parental", "Short estilo Vox para mães e pais".
- Fonte pode ser tema, reportagem, artigo, roteiro, áudio, vídeo de apresentador ou fotografias autorizadas.
- Para um roteiro já produzido por `foco-motion-tiktok`, reaproveite apenas conteúdo validado e converta a linguagem para **colagem 2D**. Não substitua o estilo 3D dessa outra skill.
- Não usar para vídeos horizontais, longos, diagnósticos individuais, conselhos clínicos personalizados, conteúdos falsos ou replicação da identidade visual exata de outro veículo.

## Entradas e decisões padrão
- Obrigatório: `tema` OU `roteiro` OU `fonte` OU `audio`.
- `marca`: Meu Bebê em Foco; `idioma`: pt-BR; `saida`: MP4 vertical 1080x1920 30fps, H.264/AAC, quando as dependências estiverem disponíveis.
- `duracao_alvo`: 65–80s, ajustável para Shorts mais curtos; nem duração nem formato garantem monetização.
- `formato`: noticia-explicada, mito-ou-fato, passo-a-passo, desenvolvimento, historia-curta. Inferir do tema.
- `publico`: mães, pais e cuidadores. Informar faixa etária apenas quando relevante e comprovada.
- `modo`: tópico para colagens (B-roll); vídeo de locutor com recortes por cima (A-roll, exige pipeline de vídeo já disponível); foto autorizada ancorada na colagem (C-roll).
- `assets`: fontes, recortes e trilhas autorizadas. Se faltarem, pedir o indispensável, usar placeholders identificados para prévia ou produzir especificação de assets; não inventar que foram gerados.

## Entregáveis
```text
<projeto>/
  brief.md                 pergunta, público, limitação e revisões
  fontes.md                alegação, fonte, data e status da verificação
  roteiro.md               narração limpa, ganchos e beats
  project.json             cenas, durações, camadas, textos e movimentos
  media/                   fotos, recortes e animações com direitos de uso
  audio/                   locução e música licenciada, quando houver
  render/preview.mp4       somente após render
  render/final.mp4         somente após aprovação e QA
  qa.md                    frames revisados, falhas e decisão
  publicacao.md            metadados separados para TikTok e YouTube
```
Não incluir nem afirmar a existência de arquivos não produzidos.

## Pipeline obrigatório
1. **Apuração**: determinar uma pergunta específica; checar atualidade, fonte, data do evento e contexto. Separar fatos, hipóteses e experiência pessoal. Aplicar `references/EDITORIAL.md`; orientação médica sem fonte suficiente fica bloqueada, com revisão pendente.
2. **História**: escrever 2–3 propostas de gancho e selecionar uma promessa honesta. Sequência orientativa para 75s: 0–3s gancho, 3–12s contexto, 12–35s explicação, 35–60s exemplo visual, 60–75s fechamento útil. Uma ideia central por Short.
3. **Beat map e shots**: dividir em 12–18 shots quando fizer sentido, aproximadamente 2–6s cada, variando o estado visual a cada 2–5s. Cada cena deve justificar a presença de elementos e conter narração, duração, evidências, camadas independentes e movimento. Cortes rápidos não podem prejudicar legibilidade.
4. **Direção de arte**: seguir `references/VISUAL.md`, com composição em profundidade, recortes com bordas orgânicas e cores vivas. Mostrar o argumento visualmente, não só colocar frases na tela. Para dados e texto crítico, usar camadas vetoriais/HTML no renderer, nunca depender de lettering gerado por IA.
5. **Produção econômica de assets**: priorizar recursos reutilizáveis e autorizados; depois elementos vetoriais; por último gerar ilustração ou imagem quando necessário. Não inventar fotos documentais. Separar PNGs em camadas com transparência; fundo, personagens, objetos, setas, etiquetas e números.
6. **Montagem**: construir `project.json` no contrato de `references/PRODUCAO.md`. Animar com o renderer incluso ou um compositor equivalente. Pelo menos 2 momentos devem explicar *como algo funciona* visualmente, e não apenas decorar.
7. **Áudio e legendas**: sincronizar voz com cortes a partir da gravação real. Gerar legendas com ASR/alinhamento e revisar palavra por palavra. Música instrumental deve ser licenciada e ficar abaixo da voz. SFX curtos de papel, estalo leve, rabisco e transição não devem soar infantiloides ou excessivos. Se não houver áudio, a prévia deve ser marcada como silenciosa.
8. **Prévia e QA**: rodar validação do JSON, renderizar prévia, extrair frames de início, cortes, textos e fim. Revisar cortes, legibilidade, segurança de imagens de crianças, vozes, precisão de fontes, timing, margens de interface e áudio. Corrigir e renderizar `final.mp4`. Nada de loops artificiais para alongar.
9. **Aprovação e publicação**: apresentar vídeo e registro de QA para aprovação humana. Reutilizar o MP4 em TikTok e Shorts, com pacote de metadados próprio por plataforma. **Não publicar automaticamente** sem autorização e integração.

## Três portões de controle
- **G1 editorial**: a pergunta e as alegações sensíveis têm evidência suficiente? Se não, reescrever, retirar ou bloquear publicação.
- **G2 visual**: produzir 2–3 quadros de referência na paleta aprovada para fixar identidade antes de gerar imagens caras. Confirmação humana quando disponível; caso contrário registrar estilo presumido e seguir só com recursos reversíveis.
- **G3 publicação**: humano revisa vídeo final, metadados, fontes, direitos de imagem e segurança infantil antes de publicar.

## Ritmo, storytelling e identidade
- Primeiro frame deve comunicar uma ação/pergunta real, nunca introdução de logo.
- O gancho promete informação útil, não culpa, medo ou um milagre.
- Colagens com camadas escalonadas, parallax suave, zoom por objeto, setas desenhadas, cards numerados, mapas ou diagramas onde ajudam.
- **A edição é rápida, não frenética**. Momentos de cuidado, perda ou vulnerabilidade pedem câmera mais lenta e pouca música.
- Headline com 2–5 palavras, sem cobrir rosto, fotografia documental ou legenda. Texto crítico deve permanecer legível.
- Final entrega resposta à pergunta inicial. CTA curto e contextual é opcional.

## Executar o renderer incluído
O starter está em `renderer/`. Seu contrato de dados e limitações estão em `references/PRODUCAO.md`.
```bash
cd skills/parental-motion-collage/renderer
npm install
npm run validate
npm run preview
npm run render
```
A amostra inclusa pode ser renderizada sem APIs, só com vetores e texto. Substitua `public/project.json` pelos dados validados do projeto; adicione mídias autorizadas em `public/media/`. **O renderer inicial NÃO gera roteiro, fotos, narração, alinhamento de legendas, transcrição, nem faz lip-sync em A-roll**; esses estágios exigem ferramentas adicionais. Não atribua essas capacidades ao código de exemplo.

## Critérios de aceite
- Saída vertical 9:16, enquadramento seguro para redes, duração real sem telas vazias.
- Fonte e data identificáveis para alegações factuais; nenhuma recomendação clínica insegura.
- Pelo menos 2 sequências de transformação visual informativa.
- 100% das palavras exibidas revisadas em pt-BR, sem distorção causada por modelo de vídeo.
- Camadas com ritmo, parallax, papel e cores consistentes; narração inteligível.
- Uso de imagem e música autorizado; rosto/foto de criança autorizado ou personagem fictício claramente ilustrativo.
- QA documentado e aprovação antes de publicação.
- Se o ambiente não suportar edição/render, entregar projeto e declarar a falha concreta, sem prometer arquivo final.

## Origem das técnicas e independência
Síntese **original**, sem copiar código-fonte dos três projetos:
- Vox Director: https://github.com/Alisa0808/vox-director (mapa de beats, prompts de colagem, câmera e separação look/motion).
- Make Vox / Faceless Shorts Creator: https://github.com/hassancs91/claude-faceless-shorts-creator (Remotion, recortes independentes, câmera global e QA por frames).
- MuAPI Director: https://github.com/Anil-matcha/vox-ai-motion-graphics-generator (pipeline de tópico a vídeo, modos B/A/C e checkpoints).
- Remotion: https://www.remotion.dev/docs

Os nomes acima indicam referência técnica; não há afiliação, licença para replicar marca, nem dependência entre os repositórios.
