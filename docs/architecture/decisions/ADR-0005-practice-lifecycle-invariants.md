---
type: adr
status: accepted
owner: project
last_verified: 2026-07-06
source_of_truth: repository
related:
  - "[[docs/architecture/decisions/README]]"
  - "[[docs/reference/PRACTICE_SCHEMA]]"
  - "[[docs/quality/DEFECTS]]"
---

# ADR-0005. Lifecycle практики имеет исполнимые инварианты

- **Статус:** accepted (2026-07-06)

## Context

Наличие статусов без правил перехода, хронологии и явной ссылки на замену не
защищает от возврата зрелой практики в `trial`, просроченной проверки или
`superseded` без доступной новой практики.

## Decision

1. Допустимые переходы:
   - `trial` → `accepted`, `deprecated`, `superseded`;
   - `accepted` → `deprecated`, `superseded`;
   - `deprecated` → `trial`, `accepted`, `superseded` после нового review;
   - `superseded` — terminal.
2. Идемпотентный переход в тот же статус разрешён.
3. Даты удовлетворяют `created <= last_verified < review_by`.
4. `superseded` требует `superseded_by`; поле пусто для других статусов.
5. `supersedes`, `superseded_by`, `conflicts_with` содержат существующие
   practice ID, не могут ссылаться на саму запись и перечисляются через запятую.
6. Replacement должен быть `trial`/`accepted`; связь двусторонняя: новая
   практика перечисляет старую в `supersedes`, старая указывает новую в
   `superseded_by`.
7. CI выполняет strict freshness как часть `make check`.

## Consequences

- Неконсистентное текущее состояние блокируется validator.
- Матрица переходов доступна review-workflow как исполнимая функция и покрыта
  тестами; проверка исторического diff остаётся ответственностью review.
- Возобновление deprecated практики требует явного нового review, а
  superseded практика не возвращается в активный lifecycle.
