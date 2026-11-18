# web-search-openrouter-agent-skill

[![CI](https://github.com/frederico-kluser/web-search-openrouter-agent-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/frederico-kluser/web-search-openrouter-agent-skill/actions/workflows/ci.yml)
[![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/frederico-kluser/web-search-openrouter-agent-skill)](https://github.com/frederico-kluser/web-search-openrouter-agent-skill/releases)

**Busca web cruzada, fontes rastreáveis e pesquisa profunda para qualquer agente — usando a chave OpenRouter do usuário.** Python 3.10+, somente biblioteca padrão, Windows/Linux/macOS. Não exige chave Exa, Firecrawl ou Tavily.

## A configuração já escolhida

Extraída da busca do Capi, iniciada no commit `7e5f7230e3617ed57b21708fdac24ab714d7b222` e evoluída em `320fbb43` e `a2b65260`:

1. **Sol Pro** (`openai/gpt-6.1-sol-pro`), raciocínio `max`.
2. **Exa** `deep-reasoning`, 25 resultados, contexto `high`, e **Firecrawl**, 10 resultados, em paralelo.
3. **Síntese pelo mesmo modelo, sem ferramenta de busca**, comparando respostas e excertos reais das citações do servidor.

É o perfil benchmarkado no projeto, não uma promessa universal de superioridade. Não há troca silenciosa por modelo barato nem benchmark novo. O modo `flash` reduz o protocolo e a quantidade de perguntas, **não** o modelo, o raciocínio nem a configuração de motores. Os parâmetros são configuráveis explicitamente.

## Instalar globalmente

```powershell
git clone https://github.com/frederico-kluser/web-search-openrouter-agent-skill.git
Set-Location web-search-openrouter-agent-skill
python scripts/install.py --all
python scripts/install.py --all --check
```

Linux/macOS: os mesmos comandos com `python3` e `cd`. O instalador cria **symlinks** para a mesma pasta canônica da skill: não copia código, não substitui instalações existentes. Detecta raízes de DSH, Claude Code (incluindo contas), Codex, Agents, Pi, JCode e OpenCode. No Windows, é necessário suporte a symlinks (Modo de Desenvolvedor ou permissões equivalentes).

Raiz personalizada: `python scripts/install.py --root /caminho/skills`. Prévia sem modificar: `--dry-run`.

A estrutura `skills/web-search-openrouter-agent-skill/` é autocontida, como skills distribuídas por plugins; também pode ser copiada para uma máquina sem o instalador. Após instalar, um agente pode invocar `/web-search-openrouter-agent-skill` (recarregue o catálogo se o harness exigir).

Opcionalmente, no Claude Code, use o marketplace incluído em vez dos symlinks:

```text
claude plugin marketplace add frederico-kluser/web-search-openrouter-agent-skill
claude plugin install web-search-openrouter-agent-skill@web-search-openrouter-agent-skill
```

Escolha um método para evitar uma skill duplicada no mesmo harness. A instalação global desta máquina usa symlinks.

## Credenciais

Defina `OPENROUTER_API_KEY` no ambiente do terminal/harness. Alternativamente, use `--env-file` para um arquivo privado. A descoberta automática fica limitada ao ambiente, arquivos dotenv do diretório atual e `~/.secrets`; nunca procura credenciais dentro de outro projeto.

```powershell
$S = "$HOME\Agent-Skills\web-search-openrouter-agent-skill\skills\web-search-openrouter-agent-skill\scripts\web_search.py"
python $S status
python $S status --check --env-file C:\caminho\privado\.env.local
```

O parser dotenv **não executa comandos**. Credenciais não são escritas na skill, no Git ou nos resultados. A chave OpenRouter paga tanto inferência quanto ferramentas de busca; configure um limite de gastos na [conta OpenRouter](https://openrouter.ai/settings/keys). Não há rotação de contas ou fallback sem chave.

## Busca simples

```powershell
python $S search "Como funciona a busca do OpenRouter?" --json
python $S search "O que o bash faz com organiza as fotos?" --out resposta.md
python $S search "Documentação oficial de pathlib" --engine exa
python $S search "Uma consulta de teste" --dry-run --json
```

Uma busca normal **não** ativa pesquisa profunda, mesmo se o texto disser "deep research". O retorno inclui resposta, citações normalizadas, motores efetivos, avisos, IDs de gerações e custo quando disponível. Se uma busca ou síntese falhar, o resultado declara a degradação; se todas falharem, termina com erro.

Citações reais vêm de `annotations.url_citation`, não de URLs que o modelo escreveu. URLs sem evidência são sinalizadas. Ter um URL não prova suporte factual: afirmações exatas, como mensagens de terminal, exigem contexto e citação literal compatíveis. O que não foi confirmado fica **não verificado**.

## Pesquisa profunda: full e flash

```powershell
# Full: kickoff OFFLINE e dossiê para condução pelo agente.
python $S search --deep-research "Qual é o estado da evidência sobre X?" --out pesquisas/x.md
python $S research init --deep-research full "Qual é o estado da evidência sobre X?" --out pesquisas/x.md

# Flash: ciclo compacto AUTOMÁTICO, com o mesmo Sol Pro/max/cross.
python $S search --deep-research flash "Como escolher entre SQLite FTS5 e BM25?" --out pesquisas/fts.md

# Full automático, com limite de rodadas explícito.
python $S research run --deep-research full "Qual é o estado da evidência sobre X?" --max-rounds 3 --out pesquisas/x-full.md

# Lint offline: formato, referências, lacunas e conclusão prematura.
python $S research lint --deep-research pesquisas/fts.md --json
```

`flash` é um perfil de **protocolo**, não um identificador de modelo e não a promessa de uma pesquisa rápida/barata. Full automático tem teto de rodadas para conter gasto; se houver lacunas, permanece parcial. O protocolo traz brief, perspectivas, FAQ, fontes `[S#]`, confiança, auditoria, verificadores adversariais e redator único. O lint estrutural e a concordância de modelos **não equivalem a verificação humana**.

Veja [o protocolo completo](skills/web-search-openrouter-agent-skill/references/pesquisa-profunda.md).

## Segurança e limites

- Escudo determinístico higieniza texto invisível e sinaliza marcadores de papel, exfiltração e instruções suspeitas. É uma defesa heurística, **não elimina prompt injection**.
- Texto da web, respostas dos pesquisadores e excertos são dados não confiáveis. Nunca se executam comandos sugeridos por fontes.
- A credencial vai somente para `https://openrouter.ai/api/v1`; redirecionamentos autenticados não são seguidos.
- `--max-bytes` limita stdout sem produzir JSON inválido. Arquivos completos usam `--out`; saídas existentes são preservadas.
- Sem browser, login em páginas, crawling irrestrito, extração integral garantida de PDFs ou verificação automática de DOI/retratações. Os excertos fornecidos pelo servidor não são necessariamente o texto integral.
- Custo desconhecido é `null`, não zero. Tokens, ferramentas e retentativas podem custar dinheiro; um limite de rodadas **não** é um teto exato em USD.

## Desenvolver e testar

```powershell
python -m unittest discover -s tests -v
python scripts/check.py
python skills/web-search-openrouter-agent-skill/scripts/web_search.py selftest
```

Os testes usam transportes falsos, sem rede ou chave. A CI testa Python e symlinks em Windows, Linux e macOS, sem consumir créditos. Consulte [CONTRIBUTING](CONTRIBUTING.md), [SECURITY](SECURITY.md) e [CHANGELOG](CHANGELOG.md).

## Origem e licença

Implementação independente em Python, com técnicas do [Capi](https://github.com/frederico-kluser/capi-animation-studio) e da [tavily-agent-skill](https://github.com/frederico-kluser/tavily-agent-skill): root-query anchoring, pesquisa por perspectivas, FAQ em árvore, auditoria de lacunas, verificação adversarial e tratamento de conteúdo não confiável. O pool de chaves Tavily não foi copiado: esta skill usa a chave OpenRouter do usuário.

[MIT](LICENSE), © 2026 Frederico Kluser. Nenhuma credencial, memória CoALA ou pesquisa privada do projeto de origem faz parte da distribuição. [Referência da API e proveniência](skills/web-search-openrouter-agent-skill/references/api.md).
