---
type: review
status: complete
owner: project
last_verified: 2026-07-07
source_of_truth: repository
related:
  - "[[docs/quality/DEFECTS]]"
  - "[[docs/how-to/HARVEST_REVIEW_APPLY]]"
---

# Phase 3 review: пользовательский knowledge route

## Scope

Проверены активные пользовательские и agent surfaces, направляющие reusable
lessons между BP и `new-project-rules`: `README.md`, canonical harvest skill и
repository contract tests.

## Решение

- Пользовательский опыт сначала становится кандидатом BP.
- Meta/process lesson нормализуется обычно в `prompts` или `common` и проходит
  тот же review, что техническая практика.
- Напрямую менять NPR из пользовательского harvest нельзя.
- Только администратор может затвердить принятую, вызревшую BP-практику через
  `promote-project-knowledge → apply-promotion-candidate`.

## Code review

- Удалён dead-end route на отсутствующий NPR skill.
- Новый contract test проверяет только active surfaces, поэтому исторические
  defect/review записи могут сохранять имя удалённого механизма как evidence.
- Canonical skill и README используют одинаковую направленность потока.
- Claude bridge не требует изменения: frontmatter canonical skill не менялся.

Блокирующих замечаний не найдено.

## Verification

- `make check`: 42 tests, validation и strict freshness passed;
- `rg` по active surfaces: retired route не найден;
- GitHub PR №4 check `validate`: passed;
- merge commit `b259ae9`: `make check` повторно passed.

## Verdict

**Approved и merged.** Исправление устраняет пользовательский dead end и
закрепляет единственный обратный knowledge flow через BP.
