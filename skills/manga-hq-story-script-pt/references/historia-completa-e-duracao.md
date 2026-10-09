# História inteira e duração de 10 a 30 minutos

O padrão é um vídeo que conta a história inteira disponível na pasta, do começo ao desfecho. A faixa desejada é aproximadamente 10 a 30 minutos, escolhida conforme a extensão e a complexidade do quadrinho. Um roteiro curto ou um trailer não substitui essa entrega. Shorts só são produzidos quando pedidos expressamente.

## Como decidir a duração

1. Leia todas as páginas e confirme a ordem de leitura. Classifique capas, publicidade e material editorial; retire esses itens do enredo, sem confundi-los com cenas da história.
2. Registre acontecimentos, motivações, consequências, mudanças de lugar e de tempo, pistas, revelações e desfecho. Preserve as relações que tornam a sequência compreensível.
3. Agrupe ações repetidas sem apagar decisões importantes. Uma cena com várias páginas pode virar um único trecho narrado; as páginas permanecem vinculadas como evidências.
4. Escreva a narração completa. Use cerca de 148 palavras/minuto como primeira estimativa, com uma faixa de 140 a 155 para planejamento. A 148 palavras/minuto, 10 a 30 minutos de narração correspondem a aproximadamente 1.480 a 4.440 palavras. A gravação final, pausas, intro e encerramento alteram a duração.
5. Ajuste a profundidade dentro do que as imagens mostram: explique contexto, objetivos, relações e consequências; abra espaço para momentos importantes e observações próprias identificadas como análise. Não invente diálogos, acontecimentos, biografia ou teorias como fatos.

Se a história disponível for realmente muito curta, declare a duração fidedigna e o motivo. Se exigir mais de 30 minutos para ser contada com clareza, preserve a história completa e explique a estimativa. Não repita frases ou imagens para preencher tempo; não acelere nem omita o final para caber no limite. Só divida em partes quando o usuário pedir. Se a pasta terminar no meio de um arco, conte todo o material disponível e diga onde ele termina, sem inventar uma conclusão além das páginas.

## Estrutura da narração

Mantenha gancho, intro/vinheta, contexto, desenvolvimento, análise/revelações, CTA e encerramento, sem anúncios. O gancho apresenta uma tensão real da obra. A intro é breve e tem identidade original. O desenvolvimento acompanha ação, decisão e consequência até o desfecho disponível. Os comentários explicam o que a obra sustenta e distinguem acusações de personagens, interpretações e acontecimentos mostrados. O CTA vem depois da entrega da história; ele não interrompe nem retém a resolução.

## Registro de cobertura no roteiro

Inclua `story_coverage` no roteiro final. O modo `complete` declara que todas as páginas classificadas como `narrative` foram revisadas e tiveram seus acontecimentos considerados. `partial` serve apenas a entregas parciais expressamente pedidas ou a um rascunho identificado; não é o padrão final.

```json
{
  "story_coverage": {
    "mode": "complete",
    "narrative_page_ids": ["P003", "P004"],
    "page_coverage": [
      {
        "page_id": "P003",
        "included_in_beats": ["B001"],
        "rationale": "A descoberta é contada no primeiro trecho da cena."
      },
      {
        "page_id": "P004",
        "included_in_beats": ["B001"],
        "rationale": "A reação conclui a mesma sequência causal."
      }
    ],
    "review_note": "Conferidos os acontecimentos e o desfecho de todas as páginas narrativas."
  }
}
```

Neste exemplo, o beat `B001` precisa apontar para cada página em sua imagem principal ou em `evidence_refs`, com painéis existentes e revisados. Uma imagem principal não precisa mudar a cada página: um beat pode reunir evidências de várias páginas enquanto exibe o painel mais expressivo. `rationale` explica o agrupamento; ela não substitui o vínculo com um beat.

O validador confere IDs, referências, revisão, exclusões e lacunas do registro. Ele não lê as imagens nem prova que uma frase representa corretamente cada acontecimento. A conferência factual da história inteira continua sendo parte do trabalho da skill. Um roteiro antigo sem esse campo continua compatível, mas não é rotulado automaticamente como completo.

## Análise entregue para a edição

`editing-analysis.json` preserva a cobertura declarada e inclui `duration_estimate`, calculado somente a partir da narração escrita. O arquivo legível mostra a contagem de palavras, a estimativa e a cobertura de página por beat. Essa estimativa nunca cria marcas de áudio: os tempos finais vêm da narração efetivamente gravada e alinhada.

O plano `visual_identity` também é preservado fielmente. O fundo deve ser original e coerente com a linguagem visual, a atmosfera e a paleta da própria HQ ou do mangá; não reutilize o antigo fundo de formas geométricas como padrão. Um arquivo relativo de fundo é resolvido a partir de `visual_identity_root`, registrado pelo exportador como a pasta de origem do roteiro. Mover a análise não altera o nome ou a semântica dos arquivos declarados; a edição pode informar uma nova raiz quando realocar o projeto.
