# Contrato do projeto de roteiro

Todos os JSONs usam UTF-8 e `schema_version: 1`. O helper lê dimensões JPG/PNG/GIF/BMP com Python padrão; Pillow ou FFprobe são fallbacks opcionais para outros formatos. Execute a partir da pasta da skill ou adapte o caminho do helper.

## Inventário

```text
python scripts/story_project.py inventory /projeto/imagens --reading-direction left-to-right --output /projeto/page-manifest.json
```

Use `--recursive` quando as páginas estiverem em subpastas. `--classify arquivo.jpg=advertisement` classifica um arquivo examinado; confira o inventário e edite as demais classes. A ordenação é natural (2 antes de 10); não deduz o sentido interno de leitura ou a cronologia da história. Cada página começa com `reviewed: false` e sem painéis: preencha após exame visual.

```json
{
  "schema_version": 1,
  "reading_direction": "left-to-right",
  "pages": [
    {
      "id": "P001",
      "file": "01.jpg",
      "status": "narrative",
      "reviewed": true,
      "width": 1200,
      "height": 1800,
      "panels": [
        {
          "id": "P001-Q01",
          "bbox": [0.05, 0.05, 0.95, 0.4],
          "description": "Descrição original da ação e dos detalhes realmente visíveis.",
          "characters": [],
          "visual_tags": ["detalhe visual confirmado"]
        }
      ]
    }
  ]
}
```

Classes: `narrative`, `cover`, `advertisement`, `editorial`. Direções: `left-to-right` ou `right-to-left`. IDs são estáveis e únicos, sem formato numérico obrigatório. `bbox` é XYXY entre 0 e 1 com x1<x2 e y1<y2. O inventário gera `file` relativo à pasta de imagens fornecida. **Registre essa pasta base no handoff e passe `--image-root /projeto/imagens` ao builder da edição** quando o manifesto ficar em `/projeto`, como no exemplo. Sem `--image-root`, o builder resolve pelo diretório do manifesto; nesse caso ajuste os paths ou salve o manifesto junto às imagens. O validador de roteiro confere a sintaxe dos paths; o builder verifica arquivos reais e hashes.

Campos adicionais, como síntese, contexto temporal, evidência e `legibility_reviewed`, podem registrar decisões editoriais. `reviewed` confirma leitura/classificação; não prova que um zoom extremo foi conferido.

## Roteiro

```json
{
  "schema_version": 1,
  "reading_direction": "left-to-right",
  "narrative_order": "source-order",
  "beats": [
    {
      "id": "B01",
      "narration": "Ele chega ao lugar onde a decisão vai mudar sua vida.",
      "page_id": "P001",
      "panel_id": "P001-Q01",
      "purpose": "gancho",
      "evidence_refs": [{"page_id": "P001", "panel_id": "P001-Q01"}]
    }
  ]
}
```

Este exemplo é apenas sintaxe, não fato de uma obra. Cada beat exige `id`, `narration`, `page_id`, `panel_id` e `purpose`. `bbox` pode ser omitida, pois está no painel; quando presente, deve ser igual à caixa do painel. Para mudar recorte, ajuste o manifesto primeiro.

`evidence_refs` é opcional e indica painéis de suporte além do exibido. Se uma fala importante precisar de várias imagens, divida em beats ou planos suficientes: referências de evidência não fazem o renderer trocar imagens automaticamente.

`narrative_order: source-order` impede regressão de páginas. Para gancho que antecipa o desfecho e depois retorna ao começo, use `editorial` e documente a mudança temporal/causal. Direção de leitura é independente desse campo. A história pode alternar presente e memória mesmo quando segue as páginas.

`narration` no nível superior é opcional; se incluída, precisa ser exatamente os textos dos beats unidos por duas quebras de linha. Não inclua rubricas, timecodes ou instruções de câmera no texto falado.

## Validação e exportação

```text
python scripts/story_project.py validate --manifest /projeto/page-manifest.json --script /projeto/script.json
python scripts/story_project.py build --manifest /projeto/page-manifest.json --script /projeto/script.json --image-root /projeto/imagens --output-dir /projeto/gravar
```

`build` cria `narration.txt`, `validated-script.json`, `editing-analysis.json` e `editing-analysis.md`. A análise inclui roteiro/manifesto, catálogo visual e planos ligados aos arquivos; veja [analise-para-edicao.md](analise-para-edicao.md). O validador rejeita referências ausentes, IDs duplicados, caixas inválidas/divergentes, página não narrativa/não revisada e rubricas evidentes na fala. Não inspeciona se uma imagem comprova semanticamente uma frase; faça essa conferência.

O inventário guarda hashes; se a pasta mudar, atualize a leitura e as evidências. A montagem exige arquivos reais e áudio alinhado. Estimativas de duração do roteiro permanecem estimativas até gravação.
