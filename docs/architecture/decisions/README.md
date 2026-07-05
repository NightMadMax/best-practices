---
type: index
status: active
owner: project
last_verified: 2026-07-05
source_of_truth: repository
related:
  - "[[docs/README]]"
  - "[[INDEX]]"
---

# Architecture Decision Records

Одно решение — один файл `ADR-<номер>-<slug>.md`. Формат: Status, Context,
Decision, Consequences. Записи не удаляются: устаревшее решение помечается
`superseded` со ссылкой на новое.

Здесь же фиксируются **крупные выборы инструментов** (почему выбрали X, а не Y);
вердикт в [[practices/tools/README]] ссылается на соответствующий ADR.

| ADR | Решение | Статус |
|---|---|---|
| [[docs/architecture/decisions/ADR-0001-provenance-required]] | Каждая запись базы несёт происхождение (проект + от кого) | accepted |
| [[docs/architecture/decisions/ADR-0002-tool-verdicts-tech-radar]] | Вердикты инструментов — по кольцам tech-radar | accepted |
| [[docs/architecture/decisions/ADR-0003-one-practice-per-file]] | Одна практика — один файл, lifecycle и evidence levels | accepted |
