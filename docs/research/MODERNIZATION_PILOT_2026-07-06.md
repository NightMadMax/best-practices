---
type: research
status: complete
owner: project
last_verified: 2026-07-06
source_of_truth: repository
related:
  - "[[docs/research/END_TO_END_PILOT_2026-07-05]]"
  - "[[docs/reference/PRACTICE_METRICS]]"
---

# Расширенный modernization pilot — 2026-07-06

## Scope

Проверены три соседних git-проекта: `Other`, `jira-analytics` и
`router-watchdog-ops`. Исходные репозитории использовались read-only; manifest
write-path проверялся на временных снимках без `.git` и без существующего
`.best-practices.json`.

## Read-only result

- 3/3 applicability reports успешно построены.
- В каждом отчёте обнаружена accepted/E2 практика `PC-2026-001`.
- Default report просмотрел `common` и все четыре cross-cutting sections.
- В исходных проектах найдено 0 consumer manifests и 0 recorded outcomes.

## Isolated write-path result

На временных снимках записаны три решения:

- `jira-analytics`: `already-compliant` — source evidence этой практики;
- `router-watchdog-ops`: `already-compliant` — source evidence этой практики;
- `Other`: `deferred` — требуется решение владельца о применимости.

Metrics result: 3 manifests, 3 decisions, 2 `already-compliant`, 1 `deferred`,
pilot adoption rate `2/3`. Временные снимки после проверки удалены.

## Ограничения

Это проверка report/record/aggregate workflow на реальных project snapshots,
но не фактическое внедрение в три репозитория. Persisted adoption остаётся
нулевым до осознанной записи manifest владельцами consumer-проектов. Нельзя
использовать pilot rate как production adoption metric.
