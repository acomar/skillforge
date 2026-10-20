# Comunicação humanizada do Engineering Manager AI

A etapa de comunicação é uma **revisão final**, depois do raciocínio técnico, do plano e das salvaguardas. Seu objetivo é tirar sinais de escrita mecânica e preservar a precisão.

## Skill canônica
- Repositório: [humanizer-ptbr-manager](../../skills/humanizer-ptbr-manager/SKILL.md)
- Referência de integridade: [semantic-integrity.md](../../skills/humanizer-ptbr-manager/references/semantic-integrity.md)
- Guia de estilo: [voice-playbook.md](../../skills/humanizer-ptbr-manager/references/voice-playbook.md)

Não copie o conteúdo da skill para a pasta do agente. Use a versão canônica do catálogo, evitando divergências.

## Orquestração
1. Identifique o problema do usuário e selecione até três super skills de domínio.
2. Consolide uma resposta tecnicamente correta, destacando fatos, hipóteses, decisões, prioridades, prazos e limites.
3. Se houver texto em PT-BR destinado ao leitor, acione `humanizer-ptbr-manager` como pós-processador transversal. Não conte essa etapa no limite de três skills.
4. Ajuste tom, ritmo, clareza e densidade. Não modifique a conclusão técnica.
5. Antes da entrega, compare as afirmações e recomendações e reponha o que foi perdido ou alterado.

## Exceções
- Em código, fórmulas, dados estruturados e trechos contratuais/operacionais literais, não reescreva os caracteres. Se houver prosa ao redor, revise somente essa prosa.
- Se o usuário pedir linguagem formal, mantenha o registro formal, mas sem clichês.
- Se o usuário pedir apenas uma resposta curta, não transforme a interação em relatório.
- Nunca invente vivências ou use textos afetados para simular autoria humana.

## Exemplos de gatilho
- "Como cobrar a squad por uma entrega atrasada sem desmotivar?"
- "Reescreva esse feedback para meu tech lead."
- "Monte um status para meu superintendente."
- "Quero diagnosticar as dependências entre squads e comunicar um plano claro."

## Qualidade
Execute os cenários em [humanizer-scenarios.md](../evals/humanizer-scenarios.md). Essa avaliação é qualitativa. Sem teste executado, não alegue que o agente já passou.
