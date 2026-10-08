# Checklist de qualidade de skills

## Identidade e ativação

- O nome é único, específico, curto e corresponde à pasta.
- A descrição diz o que a skill faz, quando deve ser usada e, se necessário, quando não usar.
- A categoria, status e versão representam corretamente a habilidade.

## Execução

- Estão claras as entradas necessárias, o procedimento e as saídas.
- Há orientações para informação insuficiente e casos de erro.
- O resultado tem critérios objetivos de aceitação.
- As dependências, integrações e permissões estão documentadas.

## Estrutura e contexto

- O `SKILL.md` guarda a lógica central, não um manual excessivamente longo.
- `references/` contém documentos lidos somente quando úteis.
- `scripts/` possui programas realmente executáveis e com instruções.
- `assets/` contém recursos necessários para a execução.
- As referências aos arquivos usam caminhos relativos e funcionam após instalação da skill.

## Segurança e portabilidade

- A skill não expõe tokens, chaves de API, senhas ou dados pessoais.
- Não assume a disponibilidade de uma ferramenta sem verificar.
- Em caso de comando destrutivo ou ação externa, respeita confirmação e autorização.
- As instruções não dependem de contexto oculto de uma conversa anterior.

## Testes e publicação

- O caso típico foi executado ou simulado conscientemente.
- Um caso ambíguo e um caso de falha foram considerados.
- O validador do repositório passou.
- Skills ainda incompletas continuam marcadas como `experimental`.
