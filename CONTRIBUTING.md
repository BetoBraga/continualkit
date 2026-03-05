# Contribuindo com ContinualKit

Obrigado pelo interesse. Antes de qualquer coisa: este é um projeto R&D-first. A qualidade do baseline importa mais que a quantidade de features.

---

## Princípios

1. **Evidência > opinião.** Toda mudança que afeta comportamento de treino ou eval precisa de benchmark comparando antes/depois.
2. **Baseline simples primeiro.** Antes de propor algo exótico (MoE, seleção inteligente de replay, adapters), o baseline simples (replay + regularização) precisa estar sólido.
3. **Sem regressão.** Se sua mudança quebra tarefas existentes sem justificativa clara, é não.

---

## Setup de desenvolvimento

```bash
git clone https://github.com/continualkit/continualkit
cd continualkit
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Verificar setup:

```bash
ruff check .           # deve retornar 0 erros
ruff format --check .  # deve retornar 0 erros
pytest                 # todos os testes passando
```

---

## Abrindo uma issue

Use os templates — eles existem por um motivo.

- **Bug:** descreva o comportamento esperado, o comportamento atual, e como reproduzir.
- **Feature:** descreva a dor que resolve, a métrica de sucesso, e o menor teste que valida a ideia.
- **`agent-ready`:** issues marcadas com essa label podem ser implementadas automaticamente pelo pipeline de agentes. Use o template específico — ele exige hipótese + critério de aceitação + scope bem definido.

---

## Abrindo um PR

1. Fork o repo e crie uma branch a partir de `main`
2. Faça suas mudanças
3. Garanta que `ruff check .`, `ruff format --check .` e `pytest` passam localmente
4. Abra o PR usando o template — todas as seções são obrigatórias
5. PRs sem testes para código novo não são aceitos

---

## Code style

- Ruff cuida de tudo: `ruff check --fix . && ruff format .`
- Type hints em funções públicas
- Docstrings em módulos e classes públicas
- Commits atômicos com mensagens descritivas

---

## O que NÃO aceitar (pra não perder tempo)

- Features sem acceptance criteria claros
- Mudanças em `.github/workflows/` sem review explícito do maintainer
- Dependências novas pesadas sem justificativa de ganho claro
- "Isso seria legal ter" sem dado de que alguém precisa disso

---

## Dúvidas

Abra uma issue com a label `question`. Resposta em melhor esforço.
