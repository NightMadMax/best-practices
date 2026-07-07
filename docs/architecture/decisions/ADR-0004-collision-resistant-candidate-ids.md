---
type: adr
status: accepted
owner: project
last_verified: 2026-07-06
source_of_truth: repository
related:
  - "[[docs/architecture/decisions/README]]"
  - "[[candidates/README]]"
  - "[[docs/quality/DEFECTS]]"
---

# ADR-0004. Новые candidate ID не требуют централизованной нумерации

- **Статус:** accepted (2026-07-06)

## Context

Последовательный ID `max + 1` вычислялся по локальной ветке. Два независимых
контрибьютора от одного `main` получали один номер, поэтому второй PR после
merge первого становился невалидным. File-per-candidate не устранял конфликт
координации идентификаторов.

## Decision

1. Новые ID имеют формат `PC-YYYY-HHHHHHHHHHHH`, где suffix — 12 lowercase
   hex characters из `secrets.token_hex(6)` (48 бит).
2. Генератор проверяет отсутствие ID в локальных `candidates/` и `practices/`
   и повторяет генерацию при совпадении.
3. Legacy ID `PC-YYYY-NNN` остаются валидными и не переименовываются.
4. ID создаёт `scripts/new_candidate.py`; ручное резервирование номера больше
   не является частью contribution workflow.

## Consequences

- Независимые ветки не координируют общий счётчик.
- Вероятность случайной коллизии практически пренебрежима для масштаба базы;
  validator всё равно запрещает дубли.
- ID становится менее удобным для устной диктовки, но остаётся коротким,
  стабильным и сортируемым по году.
