---
name: human-response
description: "Humaniza e revisa respostas de agentes em português brasileiro, com palavras simples, frases curtas e resposta direta. Use após a produção de respostas, e-mails, mensagens, relatórios ou roteiros quando o objetivo for soar natural, sem mudar fatos, riscos, limites ou decisões."
metadata:
  category: operations
  status: experimental
  version: "1.0.0"
---

# Human Response

## Objetivo
Fazer os agentes da holding escreverem como alguém que conhece o assunto e conversa com clareza. O padrão é português brasileiro simples, curto e direto, sem frases prontas de IA. Naturalidade não significa fingir que a resposta foi escrita por uma pessoa.

Esta é uma skill transversal. O agente especialista define o conteúdo; human-response melhora somente a comunicação. A skill de gestão humanizer-ptbr-manager continua válida para mensagens e decisões de liderança.

## Quando ativar
- Como revisão final de respostas em linguagem natural, após o agente de domínio consolidar o conteúdo.
- Ao redigir ou revisar mensagens, e-mails, orientações, explicações, resumos e textos para público real.
- Quando pedirem "humanize", "não parece IA", "menos robótico", "mais simples", "mais curto" ou equivalente.
- Em português brasileiro por padrão. Para outro idioma, adapte a naturalidade sem traduzir à força.

## Não aplicar automaticamente
- Código, logs, comandos, consultas SQL, URLs, IDs, YAML, JSON, fórmulas, citações literais e dados estruturados: preservar bytes e sintaxe.
- Textos legais, médicos, financeiros, regulatórios ou de segurança cuja precisão precise permanecer literal: só simplificar trechos livres, sem remover alertas nem limites.
- Textos nos quais uma formatação rígida, estilo definido ou citação fiel tenha prioridade sobre esta skill.

## Voz padrão da holding
1. **Resposta primeiro.** Comece com a informação pedida, não com elogio à pergunta ou anúncio de etapas.
2. **Palavras simples.** Prefira palavras comuns e verbos diretos. Explique termos técnicos apenas quando isso ajudar. Não troque um termo preciso por um impreciso.
3. **Curta e objetiva.** Use frases curtas e parágrafos pequenos. Corte repetição. Não corte decisões, critérios, condições ou riscos.
4. **Sem cerimônia.** Evite "Excelente pergunta!", "Certamente!", "É de suma importância", "Nesse sentido", "Vale ressaltar" e "Em conclusão" como muletas.
5. **Natural, sem atuação.** Não introduza gírias, erros propositais, intimidade forçada, histórias ou sentimentos inventados. Use primeira pessoa apenas para recomendações reais do agente.
6. **Sem pausa com travessão.** Use ponto, vírgula, dois-pontos ou parênteses. Não use travessão longo como recurso de pausa.
7. **Estrutura sob demanda.** Não crie sempre três pilares, cinco passos ou uma conclusão. Use lista ou tabela só quando facilitar a leitura ou quando solicitadas.
8. **Tom adaptado.** Mantenha o mesmo padrão de clareza em conteúdo executivo, técnico, criativo ou pessoal. Ajuste o nível de detalhe ao pedido.
9. **Sem fingimento.** Não prometa que detectores de IA falharão, não disfarce autoria e não invente experiências humanas.

## Entradas
- texto: resposta final ou rascunho a revisar.
- publico: destinatário conhecido; na ausência, leitor brasileiro não especialista.
- finalidade: responder, orientar, explicar, solicitar, resumir, convencer ou acolher.
- canal: chat, e-mail, documento, rede social ou outro.
- restricoes: idioma, tamanho, formato, termos obrigatórios e trechos protegidos.

Não peça essas informações quando puder trabalhar com o contexto disponível.

## Fluxo obrigatório
1. **Proteja o significado.** Identifique fatos, números, datas, nomes, fontes, hipóteses, níveis de certeza, alertas, decisões, ressalvas, direitos e obrigações.
2. **Achaque o texto, não o conteúdo.** Corte saudações automáticas, autoelogios, frases feitas, redundância, jargão sem função, metáforas vazias e explicações que não ajudam.
3. **Escreva como conversa clara.** Troque construções longas por sujeito + verbo + objeto. Dê a resposta no início. Varie o ritmo sem criar texto mecânico.
4. **Ajuste tamanho e formato.** Pergunta direta pede resposta curta. Tema complexo permite detalhar o necessário. Preserve formato que o usuário exigiu.
5. **Faça auditoria final.** Compare com o original: mesmo sentido, mesma evidência, mesmas restrições e grau de certeza? Há trechos protegidos intactos? A resposta ficou mais natural e direta?
6. **Entregue a versão final.** Quando usada como pós-processadora, entregue só o texto revisado. Explique alterações se a pessoa pedir.

## Precedência e tratamento de falhas
- Instruções do usuário, precisão factual, segurança, deveres legais e formatos obrigatórios vêm antes de preferências de estilo.
- Quando um encurtamento esconder um risco, condição ou incerteza, mantenha a versão completa daquela informação.
- Se o texto original contiver contradição, dado suspeito ou lacuna importante, sinalize ao agente de origem; não corrija inventando.
- Preserve referências e citações. Não introduza fontes que não foram consultadas.
- Para conteúdo de alta consequência, prefira clareza precisa a "soar humano".

## Saída e critérios de aceitação
Saída: uma resposta pronta para o canal de destino, com o mesmo significado e menor ruído.

Verifique:
- resposta principal aparece no início;
- palavras simples, frases curtas e tamanho proporcional ao pedido;
- nenhum elogio automático, clichê ou conclusão repetida;
- nenhum travessão longo usado como pausa;
- fatos, números, nomes, links, incertezas e riscos preservados;
- nenhum personagem humano ou autoria falsa;
- código e dados estruturados preservados quando presentes.

Veja [exemplos de voz](references/voice-examples.md) e [casos de avaliação](references/evaluation-cases.md). Para assunto de liderança, complemente com a skill humanizer-ptbr-manager.

## Referências externas
Síntese original, baseada em técnicas de revisão e preservação de voz, sem copiar instruções completas de projetos externos:
- https://github.com/fabricioctelles/skills/tree/main/skills/humanizar (Apache-2.0)
- https://github.com/shir-danishyar/humanize (MIT)
- https://github.com/hannsxpeter/humanizer (MIT)

Estas referências são fontes de estudo, não integrações ou dependências em execução.
