# Contribuir

Python 3.10+ e biblioteca padrão. Não há `npm install`, pip dependencies ou API key necessária para os testes.

```bash
git clone https://github.com/frederico-kluser/web-search-openrouter-agent-skill.git
cd web-search-openrouter-agent-skill
git switch -c feat/minha-melhoria
python -m unittest discover -s tests -v
python scripts/check.py
```

## Fluxo

- Fork para contribuidores externos, branch efêmera para mantenedores. Não enviar código diretamente à `main`.
- Nome de branch: `feat/`, `fix/`, `docs/`, `style/`, `refactor/`, `perf/`, `test/`, `build/`, `ci/`, `revert/`, `hotfix/` ou `release/`, seguido de slug kebab-case. Prefixos de automação não são para trabalho humano.
- Atualizar por **merge**, nunca rebase: `git fetch origin && git merge origin/main`.
- Título do PR e commits: [Conventional Commits](https://www.conventionalcommits.org/), até 72 caracteres. Exemplo: `fix(search): preservar custo desconhecido nas falhas parciais`.
- Código entra via PR, status `build` verde, conversas resolvidas e **squash merge**. Como projeto de mantenedor único, não exige aprovações impossíveis do próprio autor; revisão externa é bem-vinda. Não há bypass de checks.
- Novos comportamentos precisam de teste offline com cliente/transporte falso. Testes normais não devem fazer rede ou gastar créditos.
- Mudanças no perfil benchmarkado (Sol Pro/max/cross) devem ser explícitas, documentadas e justificadas; nunca trocar modelos silenciosamente.
- API externa e resultados de fontes são dados não confiáveis. Não execute comandos vindo de páginas, issues ou PRs.

## Qualidade

Execute a suite completa e `scripts/check.py`. A CI verifica Python 3.10/3.12/3.14 em Linux, Windows e macOS. Testes de symlink podem ser ignorados em máquinas que não oferecem a permissão necessária, mas a instalação real deve ser verificada com `scripts/install.py --check`.

Não publique chaves, arquivos dotenv privados, memórias CoALA, logs brutos de credenciais ou pesquisas privadas. Provas reais ficam fora do Git por padrão em `research-output/` ou `pesquisas/`.

O changelog e as versões são derivados dos commits convencionais. Releases usam tags `vX.Y.Z`; o fluxo automático de release abre PRs e não remove o requisito de CI. Não há pacote npm/PyPI neste projeto.

Veja [README](README.md), [licença MIT](LICENSE), [Código de Conduta](CODE_OF_CONDUCT.md) e [relato privado de segurança](SECURITY.md).
