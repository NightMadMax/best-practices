---
type: reference
status: active
owner: project
last_verified: 2026-07-07
source_of_truth: scripts/practice_metrics.py
related:
  - "[[docs/reference/PRACTICE_SCHEMA]]"
  - "[[docs/research/MODERNIZATION_PILOT_2026-07-06]]"
---

# Метрики базы и consumer outcomes

Команда:

```sh
python3 scripts/practice_metrics.py \
  --consumer /path/to/project-a \
  --consumer /path/to/project-b
```

Без `--consumer` команда показывает состав самой базы. Повторяемый
`--consumer` добавляет существующие `.best-practices.json` в агрегацию.

## Поля отчёта

- `candidate_statuses`, `practice_statuses`, `practice_sections` — состав базы;
- `evidence_levels` — распределение доказательности;
- `stale_practices` — просроченные `review_by`;
- `consumers_scanned`, `consumer_manifests_found` — покрытие потребителей;
- `consumer_outcomes`, `recorded_decisions` — реальные записанные решения;
- `consumer_preferences` — число global/section `ask` и `optout` после
  нормализации schema 1/2;
- `adoption_rate` — доля `applied` + `already-compliant` среди записанных
  решений; `null`, если решений нет.

Метрика не доказывает снижение повторяемости дефектов. Recurrence rate требует
данных source-проектов и не выводится из manifest автоматически.
