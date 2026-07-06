---
type: code-review
status: complete
owner: project
last_verified: 2026-07-06
source_of_truth: commit 2a767e4
related:
  - "[[docs/architecture/decisions/ADR-0005-practice-lifecycle-invariants]]"
  - "[[docs/reference/PRACTICE_SCHEMA]]"
  - "[[docs/quality/DEFECTS]]"
---

# Code review lifecycle invariants — 2026-07-06

## Scope

Проверен commit `2a767e4`: status transitions, chronology, supersession graph,
strict freshness, schema, review skill и tests.

## Review findings

Первый проход проверял существование `superseded_by`, но не гарантировал, что
replacement активен и ссылается обратно. До приёмки добавлены:

- replacement status только `trial`/`accepted`;
- двусторонняя связь `supersedes` ↔ `superseded_by`;
- запрет self-reference и отсутствующих practice ID;
- положительный тест полного supersession pair.

Блокирующих и неблокирующих замечаний после исправления не осталось.

## Verification

- `make check`: 37/37 tests passed.
- Обычный и strict validator: passed.
- `compileall` и `git diff --check`: passed.
- Негативно проверены chronology, missing replacement и transition matrix.
- Положительно проверена двусторонняя supersession pair.
- Legacy accepted practice мигрирована с пустым `superseded_by`.

## Verdict

**Принято.** Текущее lifecycle-состояние теперь машинно проверяется, strict
freshness входит в CI через `make check`. Исторический переход статуса остаётся
явной ответственностью review-workflow согласно ADR-0005.
