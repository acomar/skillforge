---
name: humanizer-ptbr-manager
description: "Revisa respostas e textos de gestão de engenharia em português brasileiro para ficarem naturais, específicos e claros, sem alterar fatos, decisões, riscos ou intenções. Use na etapa final do Engineering Manager AI e quando o usuário pedir revisão de tom, mensagens de liderança, feedback, e-mails ou textos corporativos."
metadata:
  category: leadership
  status: experimental
  version: "1.0.0"
---

# Humanizer PT-BR Manager

## Objetivo
Deixar a comunicação de um gestor de engenharia clara, natural e convincente pelo conteúdo, como uma conversa entre profissionais. A revisão de estilo não muda o diagnóstico nem cria fatos.

## Quando ativar
- Após a composição de respostas textuais pelo Engineering Manager AI, como uma etapa transversal de comunicação.
- Ao escrever ou revisar mensagens a squads, líderes, stakeholders, feedbacks, 1:1, diagnósticos, decisões, relatórios e planos de transformação em PT-BR.
- Quando o pedido trouxer "humanize", "não pareça IA", "deixe mais natural", "menos corporativo" ou solicitações equivalentes.

## Quando não ativar
- Para interpretar dados, escolher a estratégia, mudar um plano ou substituir super skills de domínio.
- Para reescrever comandos, código, JSON, YAML, SQL, fórmulas, IDs, URLs, nomes de arquivos ou artefatos onde caracteres e estrutura devem permanecer exatos.
- Para alterar declarações oficiais, registros legais, critérios de segurança ou mensagens de compliance que exigem texto literal. Nesses casos, preserve o texto restrito e edite apenas a explicação livre, se autorizada.

## Entradas
- `texto`: texto original ou resposta tecnicamente consolidada.
- `destinatario`: gerente, tech lead, squad, liderança executiva, parceiro, RH ou outro público, quando conhecido.
- `canal`: chat, e-mail, reunião, documento, feedback ou apresentação.
- `intencao`: informar, orientar, discordar, solicitar, alinhar, facilitar ou recomendar.
- `registro`: natural profissional por padrão; informal, executivo, didático ou formal conforme contexto.
- `restricoes`: conteúdo protegido, formato exigido e limites explícitos do usuário.

Não invente destinatário, vivência, autoridade, datas, números ou contexto ausente. Use apenas dados disponíveis.

## Procedimento
1. **Congele o conteúdo.** Identifique fatos, nomes, números, prazos, fontes, incertezas, decisões, promessas, ressalvas, responsáveis, prioridades e recomendações que devem sobreviver à revisão. Preserve também a diferença entre propostas e decisões tomadas.
2. **Identifique leitor e finalidade.** Ajuste apenas vocabulário, ordem e extensão para quem vai ler. Se não houver público definido, use PT-BR profissional, direto e acessível.
3. **Retire sinais de texto mecânico.** Corte preâmbulos vazios, entusiasmo genérico, elogios automáticos, repetição da pergunta, frases de efeito sem informação, abstrações, tríades artificiais, excesso de títulos em negrito e conclusões que repetem o parágrafo anterior.
4. **Prefira concretude comprovada.** Explique o que fazer, por que importa e qual restrição existe, utilizando exemplos ou dados já presentes. Troque jargão vago por sujeito, verbo e consequência. Mantenha termos técnicos que o público realmente usa, como backlog, deploy, CAB, DORA ou ownership.
5. **Dê ritmo humano.** Misture frases curtas e médias, varie aberturas, evite parágrafos mecanicamente simétricos e use uma voz segura sem fingir experiência própria. Não introduza erros propositais, gírias forçadas nem intimidade artificial.
6. **Respeite pontuação.** Nunca use travessão longo (`—`) como pausa. Prefira ponto, vírgula, dois-pontos ou parênteses conforme a sintaxe. Não acrescente emojis ou exclamações em contextos sérios.
7. **Adapte o tom à situação.** Feedback difícil pede precisão e respeito; reporte executivo pede síntese; conversa de equipe pede proximidade sem paternalismo; incidentes pedem informações objetivas e incerteza explícita.
8. **Audite equivalência.** Compare antes/depois: números, nomes, causas, condições, recomendações, riscos, fontes, ressalvas e níveis de certeza permanecem? A comunicação ficou mais curta sem eliminar critérios de decisão?
9. **Entregue somente a versão revisada** quando usado como pós-processador. Não acrescente cabeçalhos como "Versão humanizada", "Minha sugestão" ou lista de mudanças. Se o usuário pedir uma análise da revisão, explique as alterações separadamente.

## Regras de proteção
- Não declarar como fato algo que era hipótese, e vice-versa.
- Não transformar "recomendo", "sugiro" ou "depende" em ordem ou compromisso fechado.
- Não fabricar histórias de reuniões, projetos, emoções, aprovações, feedbacks ou experiência gerencial pessoal.
- Não remover números, requisitos regulatórios, advertências, contramétricas, riscos operacionais, segredos a proteger ou necessidade de aprovação humana apenas para deixar o texto fluido.
- Não prometer invisibilidade a detectores de IA nem afirmar autoria exclusivamente humana.
- Não modificar referências, links, blocos de código, tabelas de dados e payloads estruturados, exceto quando o usuário pedir transformação explícita.
- Em mensagens de RH, preservar dignidade, confidencialidade, critérios e distinção entre observação e julgamento.

## Saídas
- **Autônoma:** texto final revisado, mantendo o propósito e o conteúdo original.
- **Integrada ao Engineering Manager AI:** uma única resposta coerente, com as decisões técnicas e ressalvas intactas.
- **Se revisão comprometer precisão:** mantenha a formulação técnica original na parte crítica.

## Verificação
Consulte [checklist de equivalência](references/semantic-integrity.md) e [guia de voz com exemplos](references/voice-playbook.md). Na pasta `Engineering Manager/evals/humanizer-scenarios.md`, execute casos de revisão curta, feedback, métricas, mudança regulada e documentação estruturada.

## Referências e créditos
Esta implementação é uma síntese original voltada à gestão de engenharia, inspirada em princípios públicos de:
- [Humanizar: Escrita Viva em Português Brasileiro](https://github.com/fabricioctelles/skills/tree/main/skills/humanizar), licença Apache-2.0.
- [Humanizer](https://github.com/blader/humanizer), licença MIT.

Os repositórios são referências externas para aprofundamento, sem reprodução dos textos completos das skills. Esta skill não executa chamadas a essas ferramentas automaticamente.
