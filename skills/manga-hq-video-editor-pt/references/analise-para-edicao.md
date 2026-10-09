# Análise para localizar imagens na edição

A skill de roteiro entrega `editing-analysis.json` e `editing-analysis.md` junto da narração. Esses arquivos guardam a análise visual e o mapa da montagem, para a edição não precisar redescobrir qual imagem corresponde a cada frase.

## O que registrar na leitura

Em cada página: ID, arquivo, classificação, síntese e contexto temporal. Em cada painel: ID, caixa XYXY normalizada, descrição original da cena, personagens confirmados e `visual_tags` com detalhes localizáveis. Prefira pistas concretas: mão ferida, rosto em sombra, chuva na delegacia, livro de botânica. Não use nomes ou objetos que não foram reconhecidos.

Em cada beat: texto narrado, painel principal, função e `editorial_notes` explicando a escolha de imagem/foco. `evidence_refs` pode apontar painéis adicionais de apoio; não equivale a planos alternativos ou troca automática de imagem. Caso precise mostrar várias imagens durante a fala, divida a passagem em beats suficientes.

As descrições são feitas pelo agente ao examinar o material. O exporter organiza campos existentes; não usa OCR/visão nem inventa rótulos quando faltam dados. Complete descrições dos painéis usados antes de concluir; avisos de descrição ausente permanecem visíveis no arquivo.

## Exportar junto do roteiro

```text
python scripts/story_project.py build --manifest /projeto/page-manifest.json --script /projeto/script.json --image-root /projeto/imagens --output-dir /projeto/entrega
```

Saídas: `narration.txt`, `validated-script.json`, `editing-analysis.json`, `editing-analysis.md`. `image_root` aponta para a pasta das imagens relativa ao diretório da análise quando possível, ou absoluta entre volumes. A análise não copia páginas. Se o projeto for movido, mantenha essa estrutura ou forneça a nova pasta com `--image-root` na edição.

O JSON usa `schema_version:1` e `kind:"manga-hq-editing-analysis"`, com:

- `manifest` e `script`: cópias completas dos objetos revisados, para uso direto pelo editor.
- `source_fingerprints`: SHA256 dos objetos em JSON canônico (UTF-8, sort_keys, ensure_ascii=false, separators comma/colon), identificando a versão do roteiro e do inventário.
- `image_root`: base para resolver arquivos das imagens.
- `image_catalog`: páginas/painéis, arquivos, classe, sínteses, descrições, personagens e tags para busca.
- `shots`: beat→fala→arquivo→página/painel→bbox, descrição, notas de edição e `section_id` quando fornecido.
- `production_structure`: plano completo sem anúncios, quando presente no roteiro; preserva também módulos silenciosos como vinheta e cartão final. Ver [estrutura-completa-sem-anuncios.md](estrutura-completa-sem-anuncios.md).
- `story_coverage`: cobertura declarada/verificada estruturalmente das páginas narrativas e seus beats/evidências.
- `duration_estimate`: contagem do texto, estimativa de locução e meta10–30min; não são marcas do áudio.
- `visual_identity` e `visual_identity_root`: direção de arte original da obra e base dos arquivos de fundo.
- Avisos/limites: dados faltantes e necessidade de alinhar ao áudio gravado.

O Markdown mostra planos e catálogo, inclui links para imagens e identifica páginas excluídas. Use busca por nome, ação ou detalhe; confira a imagem encontrada antes de escolhê-la. Anúncios podem constar no catálogo para identificação, mas nunca são selecionados como planos narrativos.

## Usar na edição

```text
python scripts/build_timeline.py --analysis /projeto/entrega/editing-analysis.json --audio /projeto/narracao.wav --alignment /projeto/alignment.json --output /projeto/timeline.json
```

O JSON substitui a necessidade de passar `--manifest` e `--script` separadamente. O editor confere fingerprints e se os planos correspondem aos IDs, arquivos, falas e caixas embutidos; verifica também mídia real e hashes.

A revisão de leitura do roteiro não certifica o zoom final. Se os recortes/movimentos ainda não tiverem `legibility_reviewed:true`, o agente editor deve examiná-los e então usar `--confirm-legibility` no caminho `--analysis`. Essa opção registra a revisão editorial no plano em memória, sem alterar a análise original. Ela não confirma tempos: alinhamento do áudio continua obrigatório para master, e `--draft` continua estimativa de prévia.

Se só a pasta mudou, use `--image-root` para realocar as mesmas imagens. Se mudar roteiro, painel, arquivo ou bbox, atualize as fontes e gere nova análise. Não edite o mapa de planos mantendo fingerprints de outra versão.

O exporter não cria timestamps finais, voz, trilha ou câmera a partir do texto. Consulte [historia-completa-e-duracao.md](historia-completa-e-duracao.md) e [identidade-visual-da-obra.md](identidade-visual-da-obra.md) para preencher a cobertura e a direção de arte dos novos projetos. Campos de câmera já escolhidos podem ser preservados, mas a edição decide movimento e sincronismo com o áudio efetivo.

O mapa preserva endpoints e `motion.easing` propostos pelo roteiro. A edição aceita `smoothstep` (padrão) ou `linear`, valida a escolha e mantém endpoints explícitos; na ausência de câmera definida, planeja uma amplitude dinâmica conforme a duração real do beat. Curva e escala não confirmam sincronismo nem substituem a revisão visual.
