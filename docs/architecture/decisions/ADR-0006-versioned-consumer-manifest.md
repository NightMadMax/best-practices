---
type: adr
status: accepted
owner: project
last_verified: 2026-07-07
source_of_truth: scripts/practice_report.py
related:
  - "[[docs/architecture/decisions/README]]"
  - "[[docs/reference/PRACTICE_SCHEMA]]"
  - "[[docs/reference/PRACTICE_METRICS]]"
  - "[[docs/quality/DEFECTS]]"
---

# ADR-0006. Consumer manifest разделяет preferences и practice outcomes

- **Статус:** accepted (2026-07-07)

## Context

BP schema 1 хранила только per-practice outcomes, тогда как NPR onboarding
описывал несовместимые top-level `optout` и секционное `applied`. Секционное
`applied` дополнительно скрывает новые практики, появившиеся после предыдущего
review раздела.

## Decision

1. Текущий consumer contract — schema 2 с обязательными `preferences` и
   `practices`.
2. `preferences.global` и значения `preferences.sections` принимают только
   `ask` или `optout`.
3. Применение фиксируется только per-practice outcomes; секционного `applied`
   нет.
4. Loader нормализует canonical schema 1 и legacy schema 1 `optout=true` в
   schema 2 только в памяти, не изменяя consumer repository.
5. Неизвестные legacy поля, включая `applied`, не угадываются и требуют
   migration review.
6. Новые manifests создаются как schema 2. Запись outcome в canonical schema 1
   временно сохраняет schema 1 до отдельной fingerprinted migration; legacy
   optout нельзя неявно превратить записью outcome.

## Consequences

- Global/section opt-out становится совместимым с per-practice журналом.
- Новая практика остаётся видимой, даже если остальные практики раздела уже
  рассмотрены.
- A1 остаётся backward-compatible и read-only для существующих manifests;
  фактическая миграция consumer-файлов выполняется отдельной фазой A2.
- NPR writer обязан перейти на schema 2 отдельным cross-repository изменением.
