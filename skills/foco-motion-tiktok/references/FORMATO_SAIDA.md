# Formato de saída do Foco Motion TikTok

A saída padrão contém uma explicação curta para o humano, um roteiro TTS sem instruções dentro do texto falado e uma estrutura de produção.

## Estrutura de alto nível do JSON

```json
{
  "skill": "foco-motion-tiktok",
  "versao": "1.0.0",
  "fonte": {
    "plataforma": "TikTok Creator Search Insights",
    "aba": "Sugerido",
    "assuntos_extraidos": [
      {
        "busca_exata": "rotina real de maternidade em casa",
        "indicador_exibido": "195K",
        "variacao_exibida": null,
        "sinal": "teve um bom desempenho",
        "confianca_leitura": "alta"
      }
    ]
  },
  "episodio": {
    "id": "foco-001",
    "serie": "Maternidade Sem Filtro",
    "assunto": "rotina real de maternidade em casa",
    "premissa": "Uma mãe atravessa a madrugada e descobre uma forma mais simples de organizar a rotina de sono, sem prometer noites perfeitas.",
    "publico": "pessoas que cuidam de bebês",
    "faixa_etaria": "não especificada",
    "formato": "9:16",
    "resolucao": "1080x1920",
    "fps": 30,
    "duracao_total_s": 75,
    "busca_alvo": "rotina real de maternidade em casa",
    "ganchos": ["...", "...", "..."],
    "gancho_escolhido": "...",
    "perfil_voz": "Narrador empático e natural. Não incluir no texto a ser narrado.",
    "tts_text": "Texto limpo das falas de todas as cenas em sequência.",
    "cenas": [
      {
        "id": 1,
        "inicio_s": 0,
        "fim_s": 3,
        "duracao_s": 3,
        "ato": "gancho",
        "objetivo_de_retencao": "Abrir uma situação imediatamente reconhecível",
        "narracao": "São duas e dezessete.",
        "texto_tela": "02:17 DA MANHÃ",
        "visual": "Mãe cansada olhando para o relógio no quarto, berço seguro ao fundo.",
        "movimento_camera": "Travelling curto do relógio para o rosto.",
        "motion_design": "Dígitos do relógio iluminam e congelam no ar por 0,4 s.",
        "prompt_visual": "Vertical 9:16 cinematic 3D... No text baked into the image.",
        "sfx_musica": "Clique baixo do relógio; trilha minimalista a -20 dB abaixo da voz.",
        "transicao": "Match cut para o travesseiro.",
        "restricoes": ["Sem objetos soltos dentro do berço", "Sem choro de bebê excessivamente dramático"]
      }
    ],
    "publicacao": {
      "titulo": "...",
      "legenda": "...",
      "hashtags": ["#maternidade", "#rotinacombebe", "#meubebeemfoco"],
      "capa_texto": "...",
      "cta": "..."
    },
    "qualidade": {
      "conteudo_original": true,
      "revisao_especializada_pendente": false,
      "fontes_verificadas": [],
      "riscos_e_observacoes": [],
      "metricas_para_validar": ["retencao_1s", "tempo_medio", "conclusao", "views_qualificadas", "rpm"]
    }
  }
}
```

## Regras de serialização

- `inicio_s`, `fim_s` e `duracao_s` são números, nunca strings do tipo `00:03`.
- Primeira cena começa em `0`; cada cena começa exatamente quando a anterior termina.
- Último `fim_s` deve ser igual a `duracao_total_s`.
- `tts_text` é a concatenação literal de `cenas[].narracao` separada por espaços. Não incluir o perfil de voz nem instruções técnicas.
- `texto_tela` é curto e pode ser `""` se não houver texto visível.
- `fonte.assuntos_extraidos` contém apenas assuntos efetivamente legíveis, sem números supostos.
- Sem campos de projeção inventada (`views_esperadas`, `rpm_garantido`, `chance_de_viralizar`).
- Evitar prompts que obriguem o gerador de imagem a escrever textos complexos; texto final deve ser composto na edição.
- Quando solicitado modo `somente_json`, retornar apenas o objeto validado, sem explicações ou cercas markdown.

## Checks automáticos sugeridos

- `duracao_total_s > 60` e duração consistente com a soma das cenas.
- 12 a 18 cenas sugeridas para vídeo de ~75 s.
- Textos de cada cena completos, sem `TBD` ou `...` na saída final.
- Mínimo de duas cenas com Motion Design explicativo verdadeiro.
- Nenhuma recomendação sensível sem checagem adequada.
