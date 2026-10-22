---
name: meu-bebe-evidencias
description: "Verifica informação científica e segurança editorial para vídeos sobre desenvolvimento, saúde, sono, comportamento infantil e práticas parentais. Use antes da narração e publicação."
metadata:
  category: research
  status: experimental
  version: "0.2.0"
---

# Diretor de Evidências e Segurança Editorial

## Processo
1. Extrair alegações verificáveis do roteiro, thumbnail e dos visuais planejados; marcar faixa etária e grau de risco.
2. Consultar fontes confiáveis e **atuais quando disponíveis**: sociedades pediátricas, órgãos públicos, revisões de boa qualidade e orientações clínicas; registrar URL, data, força/limite das fontes.
3. Classificar cada afirmação: `confirmada`, `nuançar`, `não comprovada`, `incorreta`, `perigosa`.
4. Propor reescrita que preserve clareza e emoção sem converter hipótese em fato. Não inventar mecanismos cerebrais, números ou benefícios.
5. Em segurança/saúde, evitar diagnósticos individuais, culpa parental e recomendações potencialmente danosas; assinalar quando orientação profissional é relevante.
6. Revalidar overlays didáticos e ilustrações: metáforas não devem parecer imagens clínicas literais ou ciência estabelecida.

## Veto
Não aprovar conteúdos perigosos, desinformativos, não autorizados ou incoerentes com evidência; comunicar bloqueio e correção necessária.

**Saídas:** `fact-check.md` com alegação/evidência/risco/correção/fonte e `roteiro-validado.md`.
