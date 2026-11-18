# Pesquisa profunda — full e flash

Este protocolo é ativado **somente pela flag `--deep-research`**. Sem a flag,
`search` é busca simples, mesmo quando a consulta contém “deep research”.
`research init`, `lint` e `run` recusam a invocação sem a flag.

O nome **flash descreve o ciclo compacto**, não um modelo barato. Ambos os
perfis mantêm **Sol (`openai/gpt-6.1-sol`), raciocínio `max`, Exa
`deep-reasoning` 25/high + Firecrawl 10 em paralelo e síntese sem tools**.
Os motores e o fluxo cruzado são os escolhidos no Capi; Sol/max é a escolha
explícita do usuário para esta distribuição, não Pro. Os motores não são
reavaliados nem substituídos silenciosamente. No protocolo profundo, um
`--engine` diferente de `cross` é recusado antes de rede; use busca simples
para escolher outro motor. Modelo, esforço e provider podem ser alterados
explicitamente, nunca por inferência do termo flash.

## 1. Entrada, artefatos e custos

Os caminhos `scripts/` são relativos à **raiz da skill distribuída**, não ao
projeto em que o agente está trabalhando. Exemplos assumem essa raiz como cwd;
para uso global, use o caminho absoluto do script instalado.

```powershell
# Kickoff OFFLINE, com brief e FAQ, sem chamadas nem créditos.
python scripts/web_search.py search --deep-research "pergunta principal" --out pesquisas/tema.md
python scripts/web_search.py research init --deep-research full "pergunta" --out pesquisas/tema.md

# Flash automático: planeja, pesquisa, verifica, audita e sintetiza.
python scripts/web_search.py search --deep-research flash "pergunta" --out pesquisas/tema-flash.md --json

# Full automático: iteração limitada, três votos por afirmação.
python scripts/web_search.py research run --deep-research full "pergunta" --max-rounds 3 --workers 3 --max-questions 6 --out pesquisas/tema-full.md

# Lint offline: não consome créditos nem pesquisa novamente.
python scripts/web_search.py research lint --deep-research pesquisas/tema-flash.md --json

# Inspecionar a execução planejada sem rede nem arquivos.
python scripts/web_search.py search --deep-research flash "pergunta" --dry-run --json
```

- Cada execução grava **um dossiê `.md` e um `.evidence.json`** com o mesmo
  nome-base. Sem `--out`, os dois ficam em `pesquisas/` do **cwd do usuário**.
- Arquivos existentes nunca são sobrescritos; a colisão é verificada **antes**
  de requests pagos. Escolha outro `--out` para uma nova execução.
- O modo kickoff não fez pesquisa: sua FAQ está aberta e seu custo é zero.
- `--max-rounds` limita rodadas, **não dólares**. Full padrão: 3 rodadas,
  6 perguntas e 3 trabalhadores. Flash: 1 rodada, no máximo 3 perguntas e
  1 afirmação central por pergunta. O modelo pode fazer várias buscas por
  chamada e o custo de cada uma depende de tokens e buscas realmente usados.
- `--workers` limita trabalhadores Python. Cada busca cruzada usa dois
  motores simultaneamente; isso pode criar mais requests do que trabalhadores.
- Custo integral desconhecido é `null`; `known_cost` mostra só a parte
  conhecida. `searches` é `null` se alguma busca não informou a contagem.
  Planejador, crítico e redator não têm tools: suas contagens são zero.
- Exaurir rodadas com lacunas deixa `estado: em-curso`, preserva as evidências
  e retorna **exit 1**, sem fingir conclusão. Kickoff retorna 0. Lint com
  bloqueios retorna 1. Erros operacionais são legíveis, sem traceback/segredos.

## 2. O que vem das técnicas Tavily

A adaptação preserva as técnicas, não o pool de chaves nem a API Tavily:

1. **Brief primeiro:** objetivo, âmbito, critérios observáveis e perspectivas.
2. **Perspectivas × facetas:** perguntas atómicas, prioridades e dependências.
3. **Contextos separados por papel:** investigadores, crítico, verificadores
   e um redator. Somente o orquestrador Python grava o dossiê.
4. **Pergunta-raiz em cada contexto:** lacunas precisam justificar a relação
   com a raiz e com um critério. Texto web não define o novo objetivo.
5. **FAQ em árvore:** Q1, Q2, Q1.1…; novas perguntas mantêm pai e origem.
6. **Evidência, não resposta de memória:** fontes reais do servidor, excertos,
   citações literais e contradições explícitas.
7. **Auditoria de lacunas e término:** alcançar um limite não fecha a pesquisa.
8. **Verificação adversarial e redator único:** tentar refutar antes de afirmar.
9. **Higiene contra injeção:** sanitização, envelopes de dados, referências
   passivas, privilegio mínimo e nenhum comando vindo das fontes.

Não há rotação de contas, bans de chaves nem modo keyless. Usa-se a chave
OpenRouter **do usuário**, com retries limitados para erros transitórios.

## 3. Papéis e ciclo automático

| Papel | Ferramentas | Retorno | Restrições |
|---|---|---|---|
| Planejador | `Client.chat`, sem tools | brief, critérios K1…, perguntas Q1… | nunca chama fontes nem inventa evidência |
| Investigador | `run_search` cruzado | JSON com fontes, afirmações e trechos | só pesquisa a pergunta atómica; não grava arquivos |
| Verificador | `run_search` cruzado, contexto novo | `sustenta`, `refuta` ou `incerto` | procura contrapontos; não confirma por padrão |
| Crítico | `Client.chat`, sem tools | cobertura dos critérios, lacunas, contradições | só usa evidência validada e pergunta-raiz |
| Redator | `Client.chat`, sem tools | ordem das afirmações sustentadas | não cria afirmações nem fontes novas |
| Bibliotecário | **procedimento manual serial** | DOI/metadados/retratações/grafo | não é executado automaticamente nesta versão |

O ciclo automático é:

```text
brief/plano → investigação concorrente → integrar fontes/trechos
             → verificar adversarialmente → atualizar FAQ
             → crítico/auditoria → lacunas/dependências → próxima rodada
             → critérios cobertos? → redator único → dossiê/evidência
```

O planejador cria um DAG. Dependências só entram numa rodada depois de a
pergunta de que dependem estar respondida. Cada investigador recebe **o brief
inteiro, com IDs e textos concretos de todos os critérios**, em um envelope de
dados. Ponteiros do plano como `criteria[0]` ou `K1` são expandidos somente com
o texto daquele critério; uma referência inexistente não autoriza inventar
critério substituto. No full, o contexto inclui respostas, afirmações sustentadas,
trechos e fontes das dependências resolvidas, inclusive pais transitivos, sem
misturar perguntas independentes. Esse contexto não substitui as citações do
servidor exigidas para novas afirmações. A investigação fixa a pergunta-raiz;
fontes e retornos de outros pesquisadores entram como **DADOS NÃO CONFIÁVEIS**.

Os prompts exigem `gaps:[]` e `contradictions:[]` quando não houver problemas
substantivos. Não devem devolver frases como “nenhuma contradição” dentro desses
arrays. O parser não apaga automaticamente o conteúdo recebido para forçar
conclusão: divergências ou lacunas retornadas continuam registradas e bloqueiam
a pesquisa até a auditoria resolvê-las.

### Full

- Até 6 perguntas por padrão; até 3 afirmações por investigação.
- Três contextos verificadores por afirmação, usando o mesmo perfil benchmarkado.
- **2/3 refutam → afirmação refutada**, nunca entra na síntese.
- Uma refutação minoritária deixa a afirmação **contestada**, com a divergência
  registrada; não vira fato só porque a maioria concordou.
- Pelo menos 2 votos que sustentam, nenhum que refuta, e trechos válidos são
  necessários para promover uma afirmação a sustentada. Voto sem trecho/URL
  real é `incerto`. Três contextos **não provam independência estatística**:
  o mesmo modelo pode reproduzir erros correlacionados.
- O crítico cria lacunas Q1.1… ligadas a critério e à pergunta-raiz. Se o limite
  de perguntas estiver cheio, **a lacuna permanece bloqueio**, não desaparece.
- Rodadas substituem a revisão ativa das afirmações da FAQ; versões anteriores
  ficam no histórico, inativas. A prontidão considera só a revisão ativa.

### Flash

- Uma rodada, no máximo 3 perguntas, uma afirmação central por pergunta.
- Um verificador adversarial com **pacote compacto de afirmações**, em contexto
  novo, procurando fontes contrárias com a mesma busca cruzada.
- Um voto `refuta` descarta a afirmação; `incerto` deixa não verificada.
- Confiança nunca sobe a `alta` no flash. Auditoria e critérios ainda precisam
  fechar; falta de cobertura retorna parcial.
- **Não equivale ao full de três verificadores**, não promete pesquisa exaustiva,
  extração integral nem validação científica completa.

## 4. Evidência e fontes

Os pesquisadores devolvem JSON com o seguinte núcleo:

```json
{
  "question_id": "Q1",
  "state": "respondida",
  "confidence": "moderada",
  "sources": [
    {
      "url": "https://fonte-publica.example/manual",
      "level": "A",
      "kind": "documentação primária",
      "basis": "Autor e método identificados no conteúdo consultado",
      "independence": "origem primária identificada"
    }
  ],
  "claims": [
    {
      "text": "Afirmação verificável, delimitada ao contexto pesquisado.",
      "sources": ["https://fonte-publica.example/manual"],
      "quotes": [
        {"url": "https://fonte-publica.example/manual", "quote": "Trecho literal da fonte retornada pelo servidor."}
      ],
      "central": true
    }
  ],
  "gaps": [],
  "contradictions": []
}
```

A URL só é aceita se constar das **annotations `url_citation` do servidor**.
Uma URL criada pelo modelo não é fonte. O trecho precisa existir no conteúdo
retornado daquela fonte, com correspondência literal normalizada por espaços
e caixa. Isso é uma verificação de **presença**, não prova de entailment ou
veracidade. O verificador ainda tenta derrubar a atribuição e o contexto.

As sínteses das buscas de **investigadores e verificadores profundos** recebem
até **6.000 caracteres por excerto**, para não perder uma passagem necessária
logo depois do prefixo curto. Esse orçamento local de contexto não troca os
motores, resultados, modelo ou esforço e não significa leitura integral; a
busca simples mantém seu padrão de 1.500 caracteres. A verificação continua
exigindo a passagem literal no conteúdo efetivamente retornado.

“Não verificado:” e “Não verificado —” são sentinelas de estado epistémico, não
afirmações factuais para votar. Se faltarem dados, o investigador deve devolver
`claims:[]` com a lacuna em `gaps`; se devolver uma sentinela como claim, ela
permanece não verificada e não dispara verificadores. Isso **não** elimina
negativas factuais legítimas, como “o método não executa essa operação”, nem
contradições substantivas.

Fontes são deduplicadas por URL, removendo rastreamento `utm_*` e fragmentos.
Recebem IDs globais `[S1]`, `[S2]`…; as afirmações recebem C1, C2… e têm seus
próprios votos. A síntese publica somente textos de afirmações sustentadas;
o redator escolhe a ordem, sem poder inventar novas frases ou referências.

### Níveis A–D e confiança

| Nível | Avaliação por conteúdo, autoria, método e origem |
|---|---|
| A | documentação/norma/estatística primária ou pesquisa revisada com evidência pertinente |
| B | relatório institucional, preprint identificável ou trabalho técnico com método |
| C | imprensa técnica ou relato com origem identificada, que exige corroboração |
| D | fórum, agregador, marketing, pista não avaliada ou autoridade desconhecida |

O domínio sozinho não determina o nível. Sem justificativa e tipo de fonte,
a classificação permanece **D**. Avaliações feitas pelo modelo são provisórias,
não substituem leitura lateral e validação humana. Fontes só D não promovem
claims; só C deixam confiança baixa e não fecham uma pergunta de alta prioridade.
Confiança alta exige evidência A/B, avaliação substantiva de independência,
verificação e ausência de lacunas. Duas URLs que repetem a mesma origem não
contam como duas fontes independentes.

Para bases académicas, consulta de metadados e bibliotecário serial, leia
[fontes-de-pesquisa.md](fontes-de-pesquisa.md). Esta versão **não consulta APIs
académicas para validar DOI, metadados ou retratações automaticamente**. O dossiê
sempre declara essa limitação. Nem uma URL DOI nem um título fornecido pelo
modelo autorizam escrever “DOI validado”.

## 5. Término e lint

Um dossiê automático só recebe `estado: concluido` se:

- todas as perguntas ativas estão respondidas com confiança moderada/alta;
- não há lacunas/contradições abertas, inclusive lacunas propostas além do teto;
- todos os critérios K1… têm evidência sustentada explicitamente auditada;
- todas as afirmações da revisão ativa passaram no protocolo de verificação;
- o crítico executou a auditoria com retorno válido.

Uma execução parcial também é útil: entrega fatos sustentados, perguntas
abertas, fontes e custos, sem apresentar ausência de evidência como prova.

O lint verifica estrutura, fontes seguras, citações fantasmas, perguntas órfãs,
estados/confiança, votos ausentes, refutações declaradas sustentadas, conclusão
prematura, divergência entre Markdown e evidência JSON, imagens Markdown
(inclusive reference-style), HTML ativo e caracteres invisíveis. O veredito
`PRONTO-PARA-SINTESE` **não é certificado de verdade científica**; é a condição
estrutural para uma síntese baseada na evidência registrada.

## 6. Segurança e limites residuais

- A chave nunca entra em prompts, JSON público ou artefatos. Credenciais
  autenticam somente a origem fixa OpenRouter; fontes não desencadeiam fetch.
- O escudo é heurístico: remove controles invisíveis/role markers e sinaliza
  instruções/exfiltração, mas **não detecta toda falsidade ou ataque adaptativo**.
- Risco alto preserva só referência/sinais, sem excerto utilizável. Risco médio
  não sustenta sozinho uma afirmação: exige fonte avaliada e sem sinais para
  corroborar. Uma fusão nunca reduz o risco de alto/médio para nenhum.
- O renderizador cria Markdown passivo: neutraliza HTML e imagens, incluindo
  imagens por referência/shortcut. Nem conteúdo retornado nem URLs são executados.
- Subperguntas novas têm justificativa explícita vinculada ao brief; isso reduz
  desvio de escopo, sem prometer que um crítico LLM nunca será manipulado.
- As verificações usam excertos fornecidos pelo servidor, não leitura integral.
  Não descreva uma página como lida na íntegra quando só houve um excerto.
- Não há retomada automática de uma execução já gravada: use um novo `--out`
  para uma nova rodada automática, ou conduza o dossiê kickoff manualmente.
  O JSON preserva o histórico dentro da execução, não um estado global de pesquisa.

Este protocolo adapta as técnicas da `tavily-agent-skill` e a busca cruzada
benchmarkada no Capi; os detalhes de origem dos motores e payloads estão em
[api.md](api.md). Testes são determinísticos e offline; validação real usa a
chave do usuário apenas quando a execução de busca é solicitada explicitamente.
