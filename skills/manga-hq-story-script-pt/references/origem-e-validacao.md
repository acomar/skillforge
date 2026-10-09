# Origem, maturidade e validação

As instruções e helpers são implementações originais. O perfil foi derivado em2026-10-09 de quatro arquivos de referência fornecidos pelo usuário, analisados com a skill `video-editing-longform-pt` do SkillForge. Os arquivos completos foram processados tecnicamente; ASR local cobre a faixa portuguesa inteira. A revisão visual usa208 amostras regulares mais intervalos densos, sem declaração de audição crítica contínua do corpus. Ver [padrao-manga.md](padrao-manga.md) e [perfil-manga.json](perfil-manga.json) para evidências, defaults e limites.

O caso real de roteiro examinou28 imagens de Batman: The Knight#1, com23 páginas narrativas e133 regiões aproximadas. Capa, propagandas e editorial foram classificados separadamente. Um roteiro original de12 beats/297palavras tem duração estimada~120s a148ppm, sem gravação criada.

Validação inicial da versão 0.1.0, Windows/Python3.13/FFmpeg8.0.1:

- Roteiro:15 testes aprovados; inventário/validate/build executados com a pasta real.
- Timeline:21 testes aprovados, com WAV real, cobertura contínua por frames, intervalos inválidos, referências, hashes, revisão e seleção de faixas.
- Renderer1.0.1:17 testes aprovados, incluindo piloto sintético de6s com duas faixas440/880Hz, escolha de880Hz, continuidade na junção, ciano/fundo/zoom visíveis, loudness AAC, hashes, retomada2/2 e alteração seletiva1/2.
- Verificação estrutural individual e criador de skills aprovados.
- Revisão independente: leitura de páginas brutas, ensaio curto, rejeição de anúncios/ordem inválida e handoff real de evidências ao builder. Silêncio sintético em modo draft não foi apresentado como áudio narrado alinhado.
- Testes das ferramentas do SkillForge:5 aprovados. O validador da coleção inteira ainda falha nos11 diretórios legados de categorias sem SKILL.md direto, falha anterior às duas skills. Não foram migradas skills fora do escopo.

Status `experimental`: não houve master narrado completo de12–20min validado editorialmente. Uma prévia visual de21s com três recortes reais de Batman foi renderizada com silêncio e tempos de rascunho para conferir fundo, tinta e movimento; não comprova sincronismo de uma gravação.

Os scripts executam inventário, checagens, montagem de marcas e renderização. Eles não leem imagens semanticamente, escrevem roteiro, transcrevem voz ou fazem forced alignment: essas decisões são executadas pelo agente com ferramentas disponíveis e revisão. Publicação inclui somente instruções, perfis e código; não contém vídeos, áudio do canal, páginas da HQ ou transcrições extensas.

Atualização 0.2.0: o roteiro exporta `editing-analysis.json` e `editing-analysis.md`, com catálogo pesquisável e mapa fala→arquivo→painel→recorte. A edição aceita o JSON diretamente, preserva os objetos de origem e identifica a revisão editorial separadamente do alinhamento do áudio.

- Exportador: 22 testes aprovados, incluindo 7 novos casos de catálogo, dados ausentes, fingerprints, links e mudança de pasta.
- Editor: 33 testes de timeline e 17 de renderer aprovados; integração exportação→consumo com PNG/WAV passou.
- Exemplo real: análise local de Batman com 28 páginas, 133 regiões e 12 beats; associação, existência e hashes das imagens conferidos. Não houve nova gravação nem novo master narrado.
- Revisão independente dos helpers e do contrato não encontrou falha material na associação. Descrições, tags e notas continuam consultivas: a montagem segue a ordem de `script.beats` e não interpreta imagens automaticamente.
- Estrutura individual e 5 testes das ferramentas do repositório aprovados. O validador global continua com os mesmos 11 diretórios legados sem `SKILL.md` direto.

Atualização 0.3.0: por preferência explícita do projeto, o padrão completo sem anúncios passa a ser a entrega padrão: gancho, intro/vinheta, contexto, recap, análise/revelações, CTA e outro. Os valores observados do corpus foram preservados; a versão 0.2.0 do perfil acrescenta decisões de aplicação.

- Exportador: 27 testes aprovados; builder: 38 testes aprovados. A estrutura completa atravessa roteiro, análise e timeline, inclusive módulos silenciosos sem inventar fala/imagem/tempo.
- Integração exportação→consumo com PNG, WAV e marcas confirmadas aprovada; seções comerciais explícitas são rejeitadas e CTA editorial permanece permitida. Arquivos antigos sem essa estrutura continuam aceitos.
- Estrutura individual e 5 testes das ferramentas do repositório aprovados. O validador global continua com os mesmos 11 diretórios legados sem `SKILL.md` direto.
- Renderer do corpo não foi alterado. Gancho/intro/outro, trilha e efeitos são executados pelo agente na composição final; registrar seções não comprova que foram renderizadas. Não houve novo master narrado completo nesta atualização.

Para repetir a partir da raiz do SkillForge:

```text
python -m unittest discover -s skills/manga-hq-story-script-pt/tests -v
python -m unittest discover -s skills/manga-hq-video-editor-pt/tests -v
python -m unittest discover -s tests -v
python scripts/validate_skills.py
```
