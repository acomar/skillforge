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

Atualização 0.4.0: o padrão passa a contar toda a história fornecida, visando 10–30 minutos conforme extensão e complexidade. O fundo é original por obra, com cores dos painéis preservadas; o antigo fundo azul com formas permanece somente como observação histórica das referências.

- Roteiro/exportador: 36 testes aprovados. A cobertura completa exige todas as páginas narrativas revisadas e ligadas aos beats ou evidências; a estimativa por palavras e a identidade visual atravessam a análise sem criar marcas de áudio.
- Builder: 54 testes aprovados, incluindo integração exportação→consumo com PNG/WAV, resolução de fundos relativos, realocação, hashes, preservação da fonte e substituição de imagem sem perder os controles de escuridão/zoom revisados.
- Renderer 1.1.0: 26 testes aprovados, com renderização real de fundo próprio, cores originais, fallback ambiente discreto, RGBA, retomada e rejeição de ativo alterado. A revisão independente incluiu um caso real com transparência.
- Nova prévia visual de Batman: 21,021s, 960×540, 630 frames, três recortes reais, fundo original gerado para esta obra e silêncio. Decodificação completa aprovada; início, meio e fim inspecionados para contraste, textura e legibilidade. Esta prévia não é um master narrado de 10–30 minutos e não comprova sincronismo de voz.
- Estrutura das duas skills, recursos relativos, JSON, pacotes e 5 testes das ferramentas do repositório aprovados. O validador global continua com os mesmos 11 diretórios legados sem `SKILL.md` direto.
- A verificação estrutural da cobertura não certifica fidelidade factual. Não houve master longo narrado revisado nesta atualização; o status continua `experimental`. Os módulos de intro/outro/mix continuam sendo executados pelo agente na composição final, além do renderer de painéis.

Atualização 0.5.0: câmera mais perceptível e suave, atendendo à revisão da prévia. A antiga amostra tinha zoom de apenas1↔1.12 em6–7s; ela não representava o default anterior do builder1↔1.8. O novo default usa1↔1.25–1.50 conforme a duração alinhada, com `smoothstep`, preservando endpoints explícitos e a duração do áudio. Fades novos começam em0.25s, mantendo os explícitos.

- Builder: 57 testes aprovados; integração real do exportador→análise→timeline confirma endpoints, easings, fontes/fingerprints intactos e duração do áudio. O helper de roteiro não foi alterado nesta versão.
- Renderer1.2.0: 31 testes aprovados, com 91 frames sintéticos consecutivos para centroide/progressão/alpha/endpoints/easing. Na fixture examinada, a oscilação do centro passou de1.46/1.45px para0.36/0.41px; esses números não são uma medida universal de qualquer vídeo. O fallback de planos diretos usa a mesma amplitude por duração do builder, preservando movimentos explícitos.
- O zoom trabalha em resolução intermediária ampliada e `gbrap`. Fator4× em960×540 e2× em1920×1080; limite3840 por eixo/~8.3MP, portanto1× emUHD. A suavidade em resoluções maiores exige revisão específica. Fundo inteiro/dividido produziu61 frames RGBA idênticos, sem reiniciar o movimento global; dithering da vinheta foi desativado.
- Alteração de easing invalida apenas o segmento correspondente; a retomada reutiliza os demais. Fontes, hashes, prontidão e faixa de áudio continuam protegidos.
- Nova amostra de Batman:18.018s,960×540,540frames, silêncio, três cenas de6s com amplitude/foco revisados. Decodificação completa aprovada e frames selecionados inspecionados; esta prévia não comprova um master narrado de10–30min.
- Estrutura individual, referências/pacotes e5 testes das ferramentas do repositório aprovados. A validação global continua com os mesmos11 diretórios legados sem `SKILL.md` direto. Status `experimental` preservado.

Para repetir a partir da raiz do SkillForge:

```text
python -m unittest discover -s skills/manga-hq-story-script-pt/tests -v
python -m unittest discover -s skills/manga-hq-video-editor-pt/tests -v
python -m unittest discover -s tests -v
python scripts/validate_skills.py
```
