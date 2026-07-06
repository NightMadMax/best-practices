---
type: research
status: proposed
owner: project
last_verified: 2026-07-05
source_of_truth: repository
related:
  - "[[AGENTS]]"
  - "[[docs/quality/DEFECTS]]"
---

# Предложение обновления AGENTS.md в следующей сессии

Активный `AGENTS.md` нельзя менять после загрузки инструкций. В новой сессии
нужно заменить только шаблонные разделы `Commands` и `Done when`.

## Commands

```markdown
## Commands

- Full local check: `make check`.
- Unit and contract tests: `make test`.
- Repository schema and link validation: `make validate`.
- Strict freshness check: `python3 scripts/validate.py --strict-freshness`.
- Metrics snapshot: `make metrics`.

`make check` уже включает strict freshness; отдельная команда полезна для
диагностики freshness без полного тестового прогона.
```

## Done when

```markdown
## Done when

- `make check` passes.
- `python3 scripts/validate.py --strict-freshness` passes.
- Candidate/practice IDs, targets, provenance and evidence levels validate.
- Relevant indexes and workflow skills stay synchronized.
- No secrets, private identifiers or machine-specific paths are introduced.
- GitHub CI passes for changes intended for merge.
```

После применения проверить бюджет instruction chain и закрыть соответствующий
дефект в `docs/quality/DEFECTS.md` отдельным commit.
