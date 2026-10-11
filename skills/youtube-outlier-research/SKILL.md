---
name: youtube-outlier-research
description: Descobre vídeos do YouTube que superam a mediana de canais comparáveis por formato, especialmente Shorts e canais pequenos, e converte os padrões comprovados em ideias originais. Use para caçar outliers, pesquisar concorrentes ou priorizar novos vídeos por evidência; não use como estimativa de receita ou analytics privados.
metadata:
  category: research
  status: experimental
  version: "0.1.0"
---

# YouTube Outlier Research

Encontre vídeos que renderam acima do padrão **do próprio canal**, não simplesmente os mais vistos do YouTube. Funciona para vídeos longos e candidatos a Shorts, em português, espanhol e inglês. A execução pode usar a YouTube Data API v3 ou um snapshot JSON offline. Responda no idioma do pedido.

## Quando usar e quando não usar

Use em pesquisa de nicho, análise de canais pequenos, inspiração de ganchos, priorização editorial e comparação de formatos vencedores. **Não use** para afirmar alcance futuro, descobrir dados privados de CTR/retenção, determinar receita real, classificar Shorts com certeza somente pela duração ou reproduzir roteiros de terceiros.

## Entradas e defaults

- Obrigatório: `--terms "assunto"` e/ou `--channel-ids UC...`, ou um `--snapshot arquivo.json` já coletado.
- Defaults: 30 dias de descoberta; até 50 mil inscritos; mínimo 10 mil views; outlier ≥3x; baseline de até 30 uploads do mesmo tipo, excluído o próprio candidato; mínimo 5 pares; pelo menos 24 horas após publicação.
- `--video-format shorts|longs|all` (padrão `all`). Duração ≤180 segundos significa somente **possível Short**, não comprovado pela API.
- Filtros úteis: `--published-after`, `--published-before` (RFC3339), `--max-subscribers`, `--min-views`, `--min-outlier-score`, `--max-duration-seconds`, `--baseline-size`, `--min-baseline`, `--max-results`, `--sort-by outlier|views|velocity`, `--search-order date|viewCount|relevance`, `--relevance-language`, `--region-code`.
- Trate `relevanceLanguage` como pista de pesquisa, **não** prova do idioma da narração. Use temas em PT/ES/EN separadamente quando a análise pedir idiomas diferentes.

## Execução

Requer Python 3.10+; o script usa somente a biblioteca padrão. Identifique `SKILL_DIR` como a pasta que contém este `SKILL.md`.

```bash
export YOUTUBE_API_KEY="SUA_CHAVE_NO_AMBIENTE"
python "$SKILL_DIR/scripts/youtube_outliers.py" \
  --terms "mangá explicado" "resumo de quadrinhos" \
  --video-format all --max-subscribers 50000 \
  --min-views 10000 --min-outlier-score 3 \
  --sort-by outlier --max-results 15 \
  --output ./outliers.json --save-snapshot ./amostra.json
```

Para inspecionar canais diretamente sem gastar cota em busca:

```bash
python "$SKILL_DIR/scripts/youtube_outliers.py" --channel-ids UCxxxxxxxxxxxxxxxxxxxxxx --output ./canal.json
```

Sem credenciais, reavalie evidências existentes:

```bash
python "$SKILL_DIR/scripts/youtube_outliers.py" --snapshot ./amostra.json --output ./reanalise.json
```

Antes de chamar a API, use `--dry-run` e confira o orçamento. A chave deve ficar em variável de ambiente; não a registre em argumentos, arquivos versionados ou relatórios. A busca `search.list` custa 100 unidades por requisição; `channels.list`, `playlistItems.list` e `videos.list` tipicamente 1 unidade por requisição. O `--quota-budget` impõe teto local **estimado**. Em caso de 403/quota, 429 ou falha de rede, reporte a falha; não invente resultados e não confunda erro com busca sem correspondências.

## Procedimento editorial

1. **Delimitar investigação.** Registre nicho, formato, região/idioma alvo, janela de publicação e restrições. Combine nicho direto, adjacente e, quando útil, outro setor com audiência parecida. Evite misturar formatos na mediana.
2. **Coletar e auditar.** Execute o script ou analise snapshot. Inspecione `candidate_count`, `sampled_channels`, `sampled_videos`, `estimated_quota_used` e `rejection_counts`. Não declare cobertura exaustiva: a busca da API é amostral/rankeada. Se muitos vídeos não atingem `min-baseline`, amplie a amostragem antes de baixar o limiar.
3. **Validar os outliers.** Confira URLs, datas, views, inscritos quando públicos, pares da mediana e escore. A fórmula é `views do vídeo / mediana de views de outros uploads do mesmo canal e formato`. Liste **separadamente** `views/subscribers` como sinal auxiliar de canal emergente, não como substituto do escore. Marque confiança limitada quando há menos de 15 pares; abaixo de 5, não classifique.
4. **Investigar por que funcionou.** Para os melhores 3 a 10, veja título, thumb, primeiros segundos, promessa, ritmo, duração, comentários e transcrição **somente quando realmente acessíveis**. Separe fatos observados de hipóteses. Sem transcrição, não atribua falas ou exemplos específicos. Considere notícia, parceria, fanbase externa, tráfego pago e idade do vídeo como possíveis confundidores.
5. **Extrair formato transferível.** Descreva a estrutura da história/gancho, não copie o tema nem a expressão criativa. Ex.: `"[personagem] fez [decisão impossível] e mudou [consequência]"`. Gere 3 adaptações originais com título, frase de thumb, gancho inicial, público e evidência do padrão. Diga quando o formato não é replicável.
6. **Priorizar por evidência.** Ordene por múltiplo e adequação ao nicho, novidade, esforço e risco autoral. Escolha um experimento barato e defina hipótese verificável. Nunca prometa viralização.

## Saída obrigatória

Entregue tabela com: vídeo (link), canal, views, inscritos (ou indisponível), data, formato/proxy, mediana, amostra (`n`), múltiplo `Nx`, confiança, razão observável/hipótese. Adicione 3 adaptações originais, sugestão principal, lacunas e quota/cobertura. O helper escreve JSON e CSV; `outliers.json` preserva métricas e rejeições para consumo pelo `viral-shorts` ou planilhas.

## Verificações e limites

- Nunca compare medianas de canais distintos como se fossem uma só; nunca conte candidato no próprio baseline; nunca use média no lugar de mediana sem sinalizar mudança metodológica.
- O YouTube fornece **views acumuladas**, não views no mesmo estágio de vida dos vídeos. `views_per_day` é proxy imperfeito, não taxa real de crescimento. Likes, retenção, CTR e receita de concorrentes não são públicos por esta integração.
- O rótulo `shorts_proxy` significa duração de até 180 s. Não configure `strict_shorts=true` sem fonte capaz de comprovar a superfície Shorts.
- Amostra insuficiente, inscritos ocultos, novos uploads, vídeos removidos, lives e filtros rigorosos explicam rejeições. Reporte essas causas antes de relaxar os critérios.
- Não copie transcrições completas, histórias, imagens ou thumbnails; use apenas análise e adaptação original. Respeite quotas, termos e direitos autorais.
- Caso normal, filtro ambíguo e falha de quota devem ter teste ou evidência; veja `references/metodologia.md` para contrato de integração e fontes.