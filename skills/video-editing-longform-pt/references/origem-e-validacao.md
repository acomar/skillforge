# Origem, melhorias e validação

## Base analisada

[gitethanwoo/video-editing](https://github.com/gitethanwoo/video-editing), título **Video Editing Skills**, no commit [`166eed9b1f391af5201a37057924593bf8f413d4`](https://github.com/gitethanwoo/video-editing/tree/166eed9b1f391af5201a37057924593bf8f413d4).

Recursos consultados: README, `skills/analyze-video-editing/SKILL.md`, seu analyzer, `skills/video-editing/SKILL.md`, seu workbench, LICENSE e NOTICE. A base separa análise, B-roll e produção, distingue medidas de interpretação e valida mídia real. Esta adaptação preserva esses princípios, reúne o fluxo voltado a vídeos longos e mantém a licença MIT de Ethan Woo em `LICENSE-upstream.txt`. O helper desta skill é uma implementação própria; não copia os scripts ou o starter Remotion da base.

## O que mudou

| Aspecto | Adaptação |
| --- | --- |
| Pedido e idioma | Português; distingue recriar montagem, adaptar estilo, editar e analisar. |
| Longa duração | Análise em capítulos com overlap, tempo global, checkpoints e cobertura explícita. |
| Retomada | Cache por hash da fonte, opções e versões; reutilização verifica artefatos. |
| Recriação | Mapa referência → fonte → saída, com diferenças e critérios de fidelidade. |
| Portabilidade | Helper de biblioteca padrão e FFmpeg/FFprobe; ASR opcional escolhido no ambiente. |
| Falhas | Retorno não-zero/timeout ficam explícitos, sem confundir falha com lista vazia. |
| Qualidade | Decode e duração separados de revisão editorial, loudness e sincronismo. |

## Maturidade

Status `experimental`. A skill não recebeu benchmark de processamento de filmes de 30–120 minutos nem validação editorial de uma recriação completa com mídia real do usuário. Não usa API de geração ou transcrição por padrão. A inspeção de amostras não substitui assistir aos intervalos relevantes; o plano de edição continua exigindo execução pelo agente ou editor escolhido.

Os comandos de teste do helper ficam em `tests/test_video_workbench.py`; sua mídia sintética é criada em diretório temporário, não integra a skill distribuída. A validação estrutural é distinta desses testes de comportamento.

## Evidências desta versão

- Validação estrutural individual do SkillForge e `quick_validate.py` do criador: aprovadas.
- Helper: 17 testes aprovados (12 de integração com FFmpeg/mídia sintética e 5 de limites/unidades), em Windows, Python 3.13 e FFmpeg 8.0.1. Compilação do Python aprovada.
- Confirmados: offset global com overlap, corte na borda sem duplicação, cobertura do último capítulo parcial, retomada sem reprocessamento, recuperação seletiva de artefato corrompido, invalidação por fonte/opções/versões, mídia inválida, duração divergente, timeout, falha simulada de detector com retomada, ferramentas ausentes e caminhos com espaços/Unicode.
- Revisão independente por simulação declarada: projeto de 48 minutos, pedido ambíguo com URL inacessível e análise com somente transcrição sem tempos. Não foram renders de filmes reais.
- Testes das ferramentas do SkillForge: 5 aprovados. O validador da coleção inteira já falhava antes desta adição, porque 11 diretórios legados de categorias não contêm `SKILL.md` diretamente. Esta entrega não migra outras skills nem altera o validador.

Para repetir os testes do helper a partir da raiz do SkillForge:

```text
python -m unittest discover -s skills/video-editing-longform-pt/tests -v
```

Os testes requerem FFmpeg e FFprobe; se ausentes, a integração é explicitamente marcada como skipped. Configure `VIDEO_WORKBENCH_TEST_TMP` com um diretório gravável caso o ambiente restrinja temporários.
