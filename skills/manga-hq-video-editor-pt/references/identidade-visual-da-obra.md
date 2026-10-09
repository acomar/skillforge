# Identidade visual original para cada obra

O padrão narrativo permanece comum; a direção de arte nasce da HQ/mangá examinada. Preserve as cores, o preto e branco e o traço dos painéis por padrão. O fundo azul com círculos e paralelogramos das versões anteriores foi substituído por um ambiente original, discreto e coerente com a obra.

## Derivar a direção de arte

Examine uma seleção representativa de páginas e cenas, além da capa: exterior/interior, luz/sombra, diálogo/ação e momentos de mudança. Registre no `visual_identity` o que está realmente presente: paleta dominante e de acento, textura do traço/papel, gênero, atmosfera, cenários recorrentes, contraste e relação entre imagem e tipografia. A identidade não deve ser deduzida apenas do nome da franquia.

Escolha um tratamento que amplifique essas características mantendo o painel como foco. Para uma HQ noir, sombras de carvão, tinta, luz âmbar discreta e atmosfera úmida podem funcionar quando apoiadas no material. Um mangá de fantasia pode pedir papel, névoa e uma cor de acento; ficção científica pode usar luz técnica e textura metálica; uma história cotidiana pode pedir papel claro e ambiente suave. São exemplos de decisão, não presets obrigatórios. Não aplique o fundo de Batman a toda obra.

Prefira um fundo original sem personagem, logotipo, balão ou acontecimento novo. É uma camada editorial de atmosfera, nunca prova narrativa. Use áreas centrais tranquilas e detalhes de baixa intensidade nas bordas. Evite ornamentos geométricos flutuantes, brilho saturado, contornos brancos, partículas decorativas constantes e elementos que concorram com rostos/texto. Ciano continua disponível como decisão específica ou pedido; não é o padrão de cor.

## Criar o recurso visual

Quando houver ferramenta de geração de imagem, crie uma imagem nova para o projeto a partir da ficha visual. Informe uso, proporção, paleta, textura, clima, centro limpo e elementos a evitar. Inspecione a imagem gerada antes de usá-la; salve-a na pasta do projeto e registre origem/prompt, dimensões e hash. Não dependa de um arquivo temporário ou de um caminho privado da ferramenta.

Exemplo de especificação adaptável: “Fundo editorial original 16:9, paleta observada nas páginas, textura discreta coerente com o traço, baixa densidade visual no centro, luz periférica suave, sem personagens, texto, marcas ou formas geométricas flutuantes.” Acrescente somente o clima reconhecido na obra. Uma fonte monocromática não exige cor inventada.

Sem gerador disponível, componha um recurso original simples com texturas próprias e luz/gradiente discreto; o renderer também oferece `ambient` com duas cores. Esse modo é alternativa técnica, e a paleta ainda precisa ser escolhida a partir da obra. A criação de fundo não altera as páginas da HQ.

O movimento do fundo é lento e secundário: um crescimento de1→1.035 ao longo da timeline é o ponto de partida do helper, configurável até1.12. Prefira planos narrativos que mostrem o fundo apenas como moldura/atmosfera. Faça fade entre painéis mantendo o ambiente contínuo. Intro, títulos, CTA e outro devem usar a mesma direção de arte, com ritmo próprio.

## Contrato e caminhos

No roteiro, o arquivo de fundo resolve a partir da pasta do roteiro:

```json
{
  "visual_identity": {
    "work": "Título da obra examinada",
    "art_direction": "Descrição original baseada nas páginas",
    "foreground_color_mode": "original",
    "background": {
      "mode": "image",
      "file": "assets/background.png",
      "darkness": 0.05,
      "zoom_from": 1,
      "zoom_to": 1.035
    }
  }
}
```

`mode:image` exige arquivo real; `sha256` esperado é opcional. `darkness` aceita0–0.65; `zoom_from`/`zoom_to` aceitam1–1.12. O renderer usa cover preservando proporção, escurecimento configurado e vinheta discreta. Fundos já escuros pedem pouca atenuação; confira no resultado.

Alternativa sem recurso externo: `background:{"mode":"ambient","palette":["#161A22","#242A34"],"darkness":0}`. A paleta contém exatamente duas cores `#RRGGBB`. Não há círculos, paralelogramos ou partículas no fundo técnico. Na falta de identidade, esse ambiente neutro permite testar a montagem; antes da entrega escolha a identidade da obra.

O exporter preserva `visual_identity` e acrescenta `visual_identity_root` relativo ao diretório da análise, apontando para a pasta do roteiro. O JSON embutido e seus fingerprints permanecem intactos. Na API, use `visual_identity_root` explicitamente quando existir um arquivo relativo; a CLI `build` registra a raiz a partir de `--script`. Uma análise sem raiz explícita exige realocação quando não for possível resolver a base com segurança.

```text
python scripts/story_project.py build --manifest /projeto/page-manifest.json --script /projeto/script.json --image-root /projeto/imagens --output-dir /projeto/entrega
python scripts/build_timeline.py --analysis /projeto/entrega/editing-analysis.json --audio /projeto/narracao.wav --alignment /projeto/alignment.json --output /projeto/timeline.json
```

Para escolher o recurso depois do roteiro, acrescente `--background-image /projeto/assets/background.png` no builder. Para realocar recursos relativos da análise sem mudar suas fontes, use `--visual-identity-root /nova/pasta-do-roteiro`. A pasta das páginas continua sendo `--image-root`, separadamente. O builder grava o caminho do fundo relativo à timeline e seu hash; um override registra a origem efetiva sem alterar o roteiro fornecido.

O plano usa `profile:comic-identity-longform-v1`. O renderer aceita também o nome de perfil legado, mas o fundo padrão atual é neutro e sem formas. `color_mode` por beat continua aceitando `original` e `manga_cyan`; o default atual é `original`. `foreground_color_mode` é direção editorial; não transforma cores automaticamente sem o agente aplicar a escolha aos beats.

## Conferir antes de finalizar

Reveja a prévia com uma imagem clara, uma escura e uma de diálogo. Fundo deve ter contraste suficiente para destacar bordas sem encobrir traços, balões ou expressões. Confira começo, meio e fim dos movimentos; uma atmosfera boa parada pode competir com o painel quando anima.

Verifique os recursos reais, hashes e resultado decodificado. Mudança no fundo invalida os segmentos em cache; nunca reutilize o render anterior ignorando a nova imagem. Arquivo ausente, hash divergente ou alteração durante o render precisa interromper a entrega, preservando as fontes.

Documente paleta, textura, clima, cor dos painéis, recurso de fundo e decisões de adaptação. Um fundo gerado não é uma nova cena da história. Uma prévia curta sem locução demonstra aparência, não cobertura completa ou sincronismo de um master de10–30min.
