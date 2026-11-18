# Fontes, leitura lateral e bibliotecário

Técnicas adaptadas da tavily-agent-skill. Este guia é do **protocolo**, não anuncia opções de CLI ou integrações que não existem.

## Descoberta → evidência → metadados

1. Descubra o panorama com busca cruzada. Varie termo técnico/leigo, inglês/idioma local, amplo/estreito, revisão/replicação/crítica.
2. Trace cada afirmação até a fonte primária, no contexto/data/versão apropriados. O excerto recebido não é necessariamente a página integral; quando faltar um detalhe, faça nova consulta específica, não complete de memória.
3. Para literatura científica central, um bibliotecário **em série** verifica DOI, título, autores, ano, publicação/retração e o grafo de citações. Esta CLI não implementa consultas diretas às APIs acadêmicas: use ferramentas HTTP separadas do harness, quando disponíveis, sem enviar a chave OpenRouter a elas. Sem essas consultas, metadados ficam explicitamente **não verificados**.

## Onde procurar

- Computação/IA: arXiv (preprints), ACL Anthology, ACM, IEEE, USENIX, DBLP, OpenReview, PMLR e JMLR; documentação primária para comportamento de ferramentas.
- Saúde: PubMed/PMC, Europe PMC, Cochrane, WHO, ClinicalTrials.gov, diretrizes e revisões sistemáticas; um preprint não tem o mesmo nível de validação de um ensaio revisado.
- Produção lusófona: SciELO, BDTD, BVS/LILACS, RCAAP.
- Dados/normas: IBGE, IPEA, BCB, INE, OECD, World Bank, Eurostat, NIST, IETF/RFC e W3C.

Exemplo de consulta (a preferência é uma instrução ao pesquisador, **não** filtro garantido do backend):

```text
Para esta pergunta, procure revisões sistemáticas no PubMed/Europe PMC e SciELO. Inclua críticas e evidência contrária; cite somente fontes retornadas pelo servidor, com excerto literal e população/período explícitos.
```

Operadores `site:` e frases entre aspas podem ajudar na consulta, mas seu tratamento depende do motor. Esta CLI não expõe os presets/filtros específicos da API Tavily.

## Bibliotecário: uma fila, não fan-out

Use uma única fila para chamadas diretas às APIs acadêmicas, respeitando os limites vigentes em seus headers e documentação. Não distribua chamadas por agentes/máquinas para contornar limites. Use cache e backoff; quando faltar acesso, procure fonte sobreposta ou declare a lacuna.

Fontes oficiais para consultar antes de implementar integração:

- [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/): DOI e metadados. [Retraction Watch via Crossref](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/): correções/retrações precisam ser interpretadas no registro do artigo e da atualização.
- [OpenAlex API](https://docs.openalex.org/): obras, autores e citações; autenticação/limites podem mudar.
- [Semantic Scholar API](https://www.semanticscholar.org/product/api): referências e citações, com limites compartilhados.
- [arXiv API terms](https://info.arxiv.org/help/api/tou.html): respeite ritmo e conexões; não contorne por paralelismo.
- [PubMed E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/), [Europe PMC REST](https://europepmc.org/RestfulWebService): biomédica e texto aberto quando disponível.

## Snowballing e independência

Depois de encontrar artigos-chave, procure o que eles citam (para trás) e quem os cita (para frente), especialmente réplicas, críticas e versões publicadas. Pare quando novas iterações não acrescentarem evidência relevante aos critérios, sem confundir saturação da consulta com cobertura universal.

Duas URLs que repetem o mesmo comunicado ou estudo contam como uma origem. Nível A–D depende de autoridade, desenho, conteúdo e contexto; o sufixo do domínio não decide. Citação literal encontrada no excerto é só uma checagem de presença: a frase ainda precisa sustentar **toda** a afirmação.

Faça leitura lateral: investigue autoria/interesses fora da página, busque melhor cobertura e trace a alegação à origem. Contradições viram perguntas de seguimento ancoradas na raiz; não suavize divergências para forçar uma conclusão. Verificadores LLM concordando podem repetir o mesmo erro.
