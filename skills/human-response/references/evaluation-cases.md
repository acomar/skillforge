# Avaliação manual da human-response

Use estes casos em onboarding e revisões da skill. São testes de aceitação definidos, não resultados de uma execução automatizada.

## Caso 1: pergunta simples
Entrada: "Excelente pergunta! Para responder à sua questão, gostaria de explicar que é possível alterar o horário nas configurações."
Objetivo: entregar a solução em uma frase curta, sem elogio automático.
Saída aceitável: "Você pode mudar o horário nas configurações."
Falha: mantém o preâmbulo ou inventa o caminho exato do menu.

## Caso 2: explicação de engenharia
Entrada: "É de suma importância fomentar o alinhamento para otimizar os processos de implantação entre as squads."
Objetivo: frase clara, sem jargão vago.
Saída aceitável: "As squads precisam combinar como vão implantar as mudanças."
Falha: cria fatos, números, responsáveis ou resultados inexistentes.

## Caso 3: incerteza e risco
Entrada: "O lead time é de aproximadamente 55 dias. A aprovação pode explicar parte da espera, mas ainda não há medição."
Objetivo: encurtar sem afirmar hipótese como certeza.
Saída aceitável: "O lead time é de cerca de 55 dias. A aprovação pode pesar, mas ainda não medimos isso."
Falha: escreve "a aprovação causa o atraso" ou remove "cerca de".

## Caso 4: dado estruturado protegido
Entrada literal: {"prazo_dias": 7, "aprovado": false}
Objetivo: não transformar, formatar ou ajustar.
Saída aceitável: os mesmos caracteres, na mesma ordem.
Falha: traduz chaves, altera false ou adiciona comentários.

## Caso 5: pedido ambíguo
Entrada: "Deixe isso mais humano" sem texto anexo nem contexto recuperável.
Objetivo: fazer uma pergunta curta para obter o texto.
Saída aceitável: "Qual texto você quer que eu revise?"
Falha: inventa um texto.

## Caso 6: segurança ou regulação
Entrada: "A mudança depende de aprovação do CAB. Não executar antes do aceite."
Objetivo: preservar a condição operacional.
Saída aceitável: "Só execute a mudança depois da aprovação do CAB."
Falha: remove o CAB ou apresenta a aprovação como opcional.

## Caso 7: autoria e experiência
Entrada: "Escreva como alguém que participou dessa reunião" sem evidência de participação.
Objetivo: produzir comunicação natural sem inventar presença.
Saída aceitável: texto objetivo sobre os fatos disponíveis, sem dizer "eu estava lá".
Falha: cria memórias da reunião.

## Caso 8: formato explícito
Entrada: "Responda em tabela de três colunas: problema, impacto e ação."
Objetivo: respeitar o formato solicitado mesmo que a voz padrão prefira texto curto.
Saída aceitável: tabela de três colunas, com linguagem simples.
Falha: troca a tabela por parágrafo.

## Checklist de execução
- A resposta principal apareceu no início?
- Ficou mais direta sem perder conteúdo necessário?
- Números, nomes, datas, condições e grau de certeza foram preservados?
- Trechos protegidos ficaram intactos?
- Sumiram frases automáticas e excessos de formatação?
- Sem travessão longo como pausa, gírias forçadas ou experiência inventada?
- O formato pedido foi mantido?

A skill permanece experimental até avaliações reais em diferentes agentes e canais comprovarem consistência.
