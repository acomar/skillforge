# Origem, maturidade e validação

As instruções e helpers são implementações originais. O perfil foi derivado em2026-10-09 de quatro arquivos de referência fornecidos pelo usuário, analisados com a skill `video-editing-longform-pt` do SkillForge. Os arquivos completos foram processados tecnicamente; ASR local cobre a faixa portuguesa inteira. A revisão visual usa208 amostras regulares mais intervalos densos, sem declaração de audição crítica contínua do corpus. Ver [padrao-manga.md](padrao-manga.md) e [perfil-manga.json](perfil-manga.json) para evidências, defaults e limites.

O caso real de roteiro examinou28 imagens de Batman: The Knight#1, com23 páginas narrativas e133 regiões aproximadas. Capa, propagandas e editorial foram classificados separadamente. Um roteiro original de12 beats/297palavras tem duração estimada~120s a148ppm, sem gravação criada.

Validação nesta versão, Windows/Python3.13/FFmpeg8.0.1:

- Roteiro:15 testes aprovados; inventário/validate/build executados com a pasta real.
- Timeline:21 testes aprovados, com WAV real, cobertura contínua por frames, intervalos inválidos, referências, hashes, revisão e seleção de faixas.
- Renderer1.0.1:17 testes aprovados, incluindo piloto sintético de6s com duas faixas440/880Hz, escolha de880Hz, continuidade na junção, ciano/fundo/zoom visíveis, loudness AAC, hashes, retomada2/2 e alteração seletiva1/2.
- Verificação estrutural individual e criador de skills aprovados.
- Revisão independente: leitura de páginas brutas, ensaio curto, rejeição de anúncios/ordem inválida e handoff real de evidências ao builder. Silêncio sintético em modo draft não foi apresentado como áudio narrado alinhado.
- Testes das ferramentas do SkillForge:5 aprovados. O validador da coleção inteira ainda falha nos11 diretórios legados de categorias sem SKILL.md direto, falha anterior às duas skills. Não foram migradas skills fora do escopo.

Status `experimental`: não houve master narrado completo de12–20min validado editorialmente. Uma prévia visual de21s com três recortes reais de Batman foi renderizada com silêncio e tempos de rascunho para conferir fundo, tinta e movimento; não comprova sincronismo de uma gravação.

Os scripts executam inventário, checagens, montagem de marcas e renderização. Eles não leem imagens semanticamente, escrevem roteiro, transcrevem voz ou fazem forced alignment: essas decisões são executadas pelo agente com ferramentas disponíveis e revisão. Publicação inclui somente instruções, perfis e código; não contém vídeos, áudio do canal, páginas da HQ ou transcrições extensas.

Para repetir a partir da raiz do SkillForge:

```text
python -m unittest discover -s skills/manga-hq-story-script-pt/tests -v
python -m unittest discover -s skills/manga-hq-video-editor-pt/tests -v
python -m unittest discover -s tests -v
python scripts/validate_skills.py
```
