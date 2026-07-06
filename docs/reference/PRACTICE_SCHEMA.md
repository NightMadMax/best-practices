---
type: reference
status: active
owner: project
last_verified: 2026-07-05
source_of_truth: scripts/validate.py
related:
  - "[[candidates/README]]"
  - "[[practices/README]]"
  - "[[docs/architecture/decisions/ADR-0003-one-practice-per-file]]"
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
`owner`, `last_verified`, `review_by`, `supersedes`, `conflicts_with` и ссылка
`candidate` на журнал решения.

- Статусы: `trial`, `accepted`, `deprecated`, `superseded`.
- `trial` требует минимум `E1`.
- `accepted` требует минимум `E2`.
- `deprecated` и `superseded` не доставляются потребителям.
- `evidence` и `evidence_level` должны совпадать со связанным accepted
  candidate. Новое подтверждение добавляется синхронно в оба файла через
  review, а не повышается только в practice.

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

Manifest создаётся в корне проекта-потребителя только явным `--record` и имеет
`schema_version: 1`. В `practices` ключом служит стабильный ID, а запись хранит
outcome, путь source practice, commit базы, дату и notes. Manifest фиксирует
решение потребителя, но не копирует содержание практики.
