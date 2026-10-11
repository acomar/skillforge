# Metodologia, integração e inspirações

## Modelo do dado

O comando `scripts/youtube_outliers.py` produz um JSON com `generated_at`, `search_terms`, `method`, `format_caveat`, `age_caveat`, `sampled_channels`, `sampled_videos`, `candidate_count`, `estimated_quota_used`, `quota_calls`, `rejection_counts` e `results`.

Cada `result` contém `video_id`, `video_url`, `title`, `published_at`, `channel_id`, `channel_name`, `channel_url`, `subscribers`, `views`, `duration_seconds`, `format`, `format_verified`, `baseline_median_views`, `baseline_sample_size`, `outlier_score`, `views_per_day`, `views_per_subscriber`, `confidence` e `caveat`. Um CSV com as mesmas colunas é gerado quando há resultados. Útil para importação pelo `viral-shorts`, sem exigir rede no processamento subsequente.

O `--save-snapshot` registra os dados normalizados `channels`, `videos` e `candidate_ids`. O `--snapshot` repete a análise offline sem consumir API. **Não** inclua chaves de API nos snapshots.

## Critérios de avaliação

- `outlier_score = views(video) / median(views(peers))`. Os pares são do mesmo canal e da mesma classe aproximada de duração, com o vídeo-alvo excluído.
- Baseline mínimo = 5; 5 a 14 pares é evidência limitada, 15+ pares melhora estabilidade mas não elimina viés.
- `views_per_subscriber` é sinal secundário do potencial de canal pequeno, não prova de descoberta orgânica ou faturamento.
- 180 segundos é corte operacional para `shorts_proxy`. Shorts reais dependem de orientação, data e classificações que esta API não entrega de forma inequívoca. Se o negócio exigir seleção estrita de Shorts, use outro sinal verificável com autorização e documente o método.
- A API de busca não permite filtrar por inscritos: descubra candidatos, consulte `channels.list`, depois aplique filtro local.
- Nunca infira causa a partir de correlação. Visualizações acumuladas favorecem vídeos mais antigos; reconheça esse viés ao comparar idades diferentes.

## Fluxo com diagnóstico de vazios

Nenhum resultado pode significar: zero vídeos encontrados, canais grandes demais, formato divergente, vídeo jovem, views insuficientes, poucos vídeos da mesma duração, mediana zero ou escore abaixo do mínimo. Consulte `rejection_counts`. Uma falha da API interrompe a execução com código 2; nunca produza uma tabela vazia fingindo sucesso de coleta.

## Fontes que inspiraram esta implementação original

- https://github.com/criscatalyst/creator-skills/tree/main/skills/outliers : mediana do canal, busca por tema, transcrição e títulos adaptados ao conteúdo.
- https://github.com/slaavass/youtube-outlier-finder : descoberta por nicho, canais pequenos, filtro local por inscritos, amostragem e diagnóstico; ideia de distinguir `views/subscribers` do outlier de vídeo.
- https://github.com/ScrapeCreators/social-media-research-skills/tree/main/skills/outlier-post-finder : normalização, mediana separada por plataforma/formato, confiança e leitura de comentários/transcrições. ScrapeCreators é opcional; a implementação local não usa sua API paga.
- https://github.com/ravsau/youtuber-skills/tree/main/skills/youtube-outliers : nichos adjacentes, identificação de estruturas transferíveis e três adaptações originais.
- Documentação oficial: https://developers.google.com/youtube/v3/docs/search/list e https://developers.google.com/youtube/v3/determine_quota_cost

Nenhum código de terceiros foi copiado. Estas fontes representam ideias metodológicas; custos, licenças, endpoints e funcionalidades podem mudar.