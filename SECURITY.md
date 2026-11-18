# Política de segurança

## Relatar em privado

Use [GitHub Private Vulnerability Reporting](https://github.com/frederico-kluser/web-search-openrouter-agent-skill/security/advisories/new). Não coloque exploits ou credenciais em issues/PRs públicos. Inclua versão/commit, reprodução mínima sem chave real, impacto e mitigação sugerida. Atendimento é best effort de um projeto de mantenedor único, sem SLA contratual. A linha de release mais recente recebe correções.

## Modelo de ameaça

Resultados web podem conter injeção indireta, links com material sensível e instruções disfarçadas de evidência. O escudo determinístico é heurístico: não elimina ataques nem confirma fatos. O modelo só recebe pesquisa e dados delimitados; esta CLI não executa comandos de páginas nem lê URLs arbitrárias com a credencial.

`OPENROUTER_API_KEY` é um segredo do usuário. A chave fica no ambiente ou arquivo privado escolhido; discovery automática é limitada ao diretório atual e `~/.secrets`. Nunca incluir arquivos privados na distribuição. A API autenticada é fixa `https://openrouter.ai/api/v1`; redirecionamentos são recusados. Não atribua à redação de segredos uma garantia que ela não tem: evite colocar segredos na pergunta e revise arquivos antes de publicá-los.

## Cadeia de fornecimento

- Biblioteca padrão Python, sem dependências de execução.
- Actions fixadas por commit SHA, permissões mínimas por job.
- Testes offline em Windows, Linux e macOS; nenhuma chave OpenRouter na CI.
- PR e check `build` obrigatórios para `main`, squash-only e tags de release protegidas.
- Secret scanning/push protection e Private Vulnerability Reporting quando disponíveis na plataforma.
- OpenSSF Scorecard monitorado; uma pontuação não substitui auditoria e não é prometida antecipadamente.

Falhas dos providers, cobrança por retries, páginas falsas ou saídas imprecisas são riscos residuais. Custos desconhecidos permanecem desconhecidos; limites de rodadas/tokens não são tetos financeiros exatos. Para orçamento real, limite os gastos da chave no OpenRouter.

Problemas não relacionados à segurança podem ser reportados nas [issues](https://github.com/frederico-kluser/web-search-openrouter-agent-skill/issues).
