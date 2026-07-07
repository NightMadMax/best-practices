---
type: reference
status: active
owner: project
last_verified: 2026-07-07
source_of_truth: scripts/practice_report.py
related:
  - "[[candidates/README]]"
  - "[[practices/README]]"
  - "[[docs/architecture/decisions/ADR-0003-one-practice-per-file]]"
  - "[[docs/architecture/decisions/ADR-0006-versioned-consumer-manifest]]"
---

# Схема кандидатов, практик и consumer manifest

Исполнимый source of truth — `scripts/validate.py`; эта страница объясняет его
контракт людям.

## Candidate

Путь новых записей: `candidates/PC-YYYY-HHHHHHHHHHHH-slug.md`, где `H` —
lowercase hex. Legacy-файлы `PC-YYYY-NNN-slug.md` остаются валидными.

Обязательные поля: `id`, `status`, `source`, `added_by`, `stack`, `target`,
`evidence_level`, `evidence`, `created`, `decided`.

- Статусы: `new`, `triaged`, `accepted`, `rejected`.
- `target` сохраняет basename в `practices/<stack>/`.
- `accepted`/`rejected` требуют `decided`; остальные требуют пустое поле.
- Harvest выставляет только `E0` или `E1`.

## Practice

Путь совпадает с basename кандидата:
`practices/<stack>/PC-YYYY-HHHHHHHHHHHH-slug.md` (либо legacy `NNN`).

Кроме provenance обязательны `tags`, `applies_to`, `does_not_apply_to`,
`owner`, `last_verified`, `review_by`, `supersedes`, `superseded_by`,
`conflicts_with` и ссылка
`candidate` на журнал решения.

- Статусы: `trial`, `accepted`, `deprecated`, `superseded`.
- `trial` требует минимум `E1`.
- `accepted` требует минимум `E2`.
- `deprecated` и `superseded` не доставляются потребителям.
- `evidence` и `evidence_level` должны совпадать со связанным accepted
  candidate. Новое подтверждение добавляется синхронно в оба файла через
  review, а не повышается только в practice.
- Даты: `created <= last_verified < review_by`.
- `superseded` требует ссылку на существующий ID в `superseded_by`; это
  terminal status. `supersedes` и `conflicts_with` также содержат существующие
  practice ID через запятую. Replacement остаётся `trial`/`accepted`, а
  `supersedes`/`superseded_by` образуют двустороннюю связь.
- Матрица переходов определена в
  [[docs/architecture/decisions/ADR-0005-practice-lifecycle-invariants]].

## Repository safety

Validator проверяет secret patterns во всех tracked и новых non-ignored
файлах. Строка тестового fixture может быть исключена только явным маркером
`secret-scan: allow` на той же строке; маркер требует review.

## Evidence levels

| Уровень | Значение |
|---|---|
| `E0` | Мнение или внешний источник без проектного подтверждения |
| `E1` | Один проект или единичный эксперимент |
| `E2` | Два независимых проекта или воспроизводимый тест |
| `E3` | Несколько проектов и повторяемая автоматическая проверка |

## `.best-practices.json`

Текущий contract — schema 2:

```json
{
  "schema_version": 2,
  "preferences": {
    "global": "ask",
    "sections": {
      "web": "optout"
    }
  },
  "practices": {}
}
```

`preferences.global` и секционные значения принимают `ask` или `optout`.
Состояния `applied` на уровне раздела нет: применение хранится только для
отдельных practice ID, поэтому новые практики не скрываются старым решением о
разделе.

В `practices` ключом служит стабильный ID, а запись хранит `outcome`, путь
source practice, 40-hex commit базы, ISO-дату и notes. Допустимые outcomes:
`applied`, `already-compliant`, `not-applicable`, `deferred`.

Loader без записи нормализует canonical schema 1 (`practices`) и legacy NPR
schema 1 (`optout=true`) в schema 2. Неизвестные поля schema 1, включая
секционное `applied`, блокируются до manual migration review. Запись нового
outcome не выполняет неявную миграцию существующего canonical schema 1.

## Applicability report

JSON report сохраняет legacy-поле `stacks` и добавляет равное ему
`detected_stacks`, а `sections` перечисляет полный набор просмотренных разделов.
По умолчанию это detected stack sections + `common` + `tools`,
`anti-patterns`, `prompts`, `snippets`.
