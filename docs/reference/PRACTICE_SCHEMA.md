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

Путь: `candidates/PC-YYYY-NNN-slug.md`.

Обязательные поля: `id`, `status`, `source`, `added_by`, `stack`, `target`,
`evidence_level`, `evidence`, `created`, `decided`.

- Статусы: `new`, `triaged`, `accepted`, `rejected`.
- `target` сохраняет basename: `practices/<stack>/PC-YYYY-NNN-slug.md`.
- `accepted`/`rejected` требуют `decided`; остальные требуют пустое поле.
- Harvest выставляет только `E0` или `E1`.

## Practice

Путь: `practices/<stack>/PC-YYYY-NNN-slug.md`.

Кроме provenance обязательны `tags`, `applies_to`, `does_not_apply_to`,
`owner`, `last_verified`, `review_by`, `supersedes`, `conflicts_with` и ссылка
`candidate` на журнал решения.

- Статусы: `trial`, `accepted`, `deprecated`, `superseded`.
- `trial` требует минимум `E1`.
- `accepted` требует минимум `E2`.
- `deprecated` и `superseded` не доставляются потребителям.

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
