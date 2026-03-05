# ContinualKit

**Atualize seu LLM sem jogar roleta russa com regressão e forgetting.**

Fine-tune incremental, eval de forgetting first-class, release gates automáticos e rollback com trilha de auditoria. Pra times que já sofreram com "funcionava ontem, hoje piorou" e não querem sofrer de novo.

---

## O problema

O ciclo típico de fine-tuning em produção é quebrado:

1. Dado novo → fine-tune rápido
2. Sobe pra prod → regressão silenciosa em tarefas antigas
3. Ninguém percebe até o suporte explodir
4. Remédio: re-treino completo — caro, lento, e você ainda não sabe o que quebrou

O gap real não é "treinar" — é **treinar sem esquecer + provar que não esqueceu**.

---

## O que é

Um toolkit Python open source que vira padrão do seu pipeline de ML:

```
continual train    # incremental com replay + regularização
continual eval     # suite de métricas de forgetting por tarefa
continual compare  # candidate vs current — diff claro antes de subir
```

Com **release gates**: o modelo não entra em prod se quebrar mais de X% em tarefas antigas.

---

## Status

**Pré-alpha — R&D em andamento.**

Os comandos existem. As implementações, não ainda. O foco agora é definir as interfaces corretas e o conjunto de benchmarks de referência.

Acompanhe no [GitHub Issues](https://github.com/continualkit/continualkit/issues) ou contribua.

---

## Quickstart

```bash
# requer Python 3.10+
pip install continualkit

# ou, pra desenvolvimento
git clone https://github.com/continualkit/continualkit
cd continualkit
pip install -e ".[dev]"

# verificar instalação
continual --version
```

---

## Roadmap

| Milestone | Foco | Status |
|-----------|------|--------|
| M1 — MVP | CLI funcional + eval suite + replay básico + integração HF/PEFT | Em andamento |
| M2 — Runtime | Storage versionado, release gates automáticos, FastAPI, pipeline n8n | Planejado |
| M3 — SOTA | MoE routing, replay inteligente, detecção de drift, políticas automáticas | Futuro |

---

## Contribuindo

Leia [CONTRIBUTING.md](CONTRIBUTING.md) antes de abrir um PR.

A regra mais importante: **sem métrica e teste de regressão, é não**. Toda feature precisa virar experimento ou gate mensurável.

Issues com a label `agent-ready` são priorizadas para implementação automática via nosso pipeline de agentes.

---

## Licença

Apache 2.0 — veja [LICENSE](LICENSE).
