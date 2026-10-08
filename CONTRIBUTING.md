# Contribuindo com o SkillForge

## Fluxo recomendado

1. Escolha uma capacidade específica que um agente precise executar repetidamente.
2. Verifique se já existe uma skill equivalente.
3. Execute o gerador de skill descrito no `README.md`, usando a categoria apropriada.
4. Escreva uma `description` clara sobre **o que fazer** e **quando usar**.
5. Preencha objetivo, entradas, processo, saídas, validações, exceções e limites.
6. Adicione `references/`, `scripts/` ou `assets/` apenas se agregarem valor real.
7. Teste a skill com um caso normal, um caso ambíguo e um caso de erro.
8. Valide com `python scripts/validate_skills.py` e rode os testes.
9. Mantenha `metadata.status: experimental` até existirem evidências de funcionamento.

## Critérios para uma boa skill

- Reutilizável: resolve uma classe de problemas, não um único pedido.
- Acionável: diz exatamente quando usar e qual resultado entregar.
- Verificável: possui critérios observáveis de qualidade.
- Segura: respeita permissões e não armazena segredos.
- Portátil: evita comandos exclusivos de uma ferramenta quando houver alternativa.
- Econômica em contexto: detalhes extensos devem ficar em `references/`.

Consulte [o checklist de revisão](skills/skillforge-maintainer/references/QUALITY-CHECKLIST.md).

## Convenções

- Pastas e nomes: `kebab-case`, sem espaços ou acentos.
- Arquivo principal obrigatório: `SKILL.md`.
- Categorias válidas: consulte `docs/CATEGORIES.md`.
- Estados: `experimental`, `stable` ou `deprecated`.
- Atualize `metadata.version` ao modificar o comportamento público da skill.
