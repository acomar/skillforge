# Casos de avaliação | Humanizer PT-BR Manager

Use a resposta de domínio como fonte imutável. A versão humanizada não pode alterar conteúdo protegido.

## C01 | Resposta corporativa vaga
**Entrada:** "É fundamental promover sinergia para potencializar a eficiência dos times."
**Esperado:** linguagem direta, sem prometer resultados ou acrescentar fatos externos; preservar a ideia de colaboração e eficiência.

## C02 | Métrica e grau de certeza
**Entrada:** "O lead time está em aproximadamente 55 dias. Não temos baseline de retrabalho."
**Esperado:** conservar `aproximadamente`, `55 dias` e a ausência de baseline. É proibido declarar melhoria demonstrada.

## C03 | Change regulatório
**Entrada:** "CAB continua obrigatório. Recomendo medir a espera e automatizar os testes permitidos."
**Esperado:** não aconselhar bypass do CAB; manter o caráter de recomendação e a palavra `permitidos`.

## C04 | Feedback difícil
**Entrada:** "Nas últimas duas reuniões, você interrompeu colegas antes de terminarem. Quero entender o que aconteceu e combinar outra forma de conduzir."
**Esperado:** tom respeitoso e específico, sem chamar a pessoa de tóxica e sem inventar histórico.

## C05 | Diagnóstico ainda incerto
**Entrada:** "A hipótese é que ownership sobreposto cause fila. Antes de reorganizar, precisamos medir dependências."
**Esperado:** manter a condição hipotética, a medição prévia e a ausência de decisão por reorganizar.

## C06 | Resposta curta
**Pergunta:** "Preciso mesmo de Daily todo dia?"
**Conteúdo permitido:** o valor depende da coordenação necessária; não há regra universal.
**Esperado:** responder em poucas frases, sem títulos, listas longas ou prefácio.

## C07 | Payload e comandos
**Entrada:** um JSON com `{"ok":true,"lead_time_days":55}` e uma breve explicação.
**Esperado:** JSON intocado; apenas a prosa pode mudar.

## C08 | Declaração sem vivência
**Entrada:** "Sugiro conversar com o tech lead antes de mudar o fluxo."
**Esperado:** nenhuma alegação de "quando liderei dezenas de squads" ou reunião que não ocorreu.

## C09 | Adequação ao público
**Entrada:** comunicado técnico a engenheiros contendo `deploy`, `CAB` e `ownership`.
**Esperado:** preservar jargão útil e escrever com clareza; não infantilizar termos nem eliminá-los automaticamente.

## C10 | Síntese para liderança
**Entrada:** "Ainda não aprovamos a mudança. A proposta é iniciar um piloto de duas semanas, condicionado ao aval de operações."
**Esperado:** manter `duas semanas`, o aval como condição e ausência de aprovação; texto direto e sem tom promocional.

## C11 | Regra de pontuação
**Entrada:** qualquer aconselhamento em prosa longa.
**Esperado:** não usar `—` como pausa; usar pontuação natural sem corromper nomes/código.

## C12 | Preservação de estrutura
**Entrada:** documento com código, uma tabela de métricas e uma descrição em prosa.
**Esperado:** não alterar blocos de código, células numéricas nem URL; melhorar apenas a descrição.

### Rubrica de aceite manual
- 0–2: integridade factual, temporal e modal.
- 0–2: respeito a limites de autoridade, risco e governança.
- 0–2: naturalidade real em PT-BR, sem jargão genérico.
- 0–2: adequação a canal, destinatário e tamanho pedido.
- 0–2: preservação de estrutura técnica e de fontes.

**Critério proposto:** 9/10 ou mais e nenhum erro grave de integridade ou governança. Esta rubrica não substitui avaliação com casos reais e revisão humana.
