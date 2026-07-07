---
type: code-review
status: complete
owner: project
last_verified: 2026-07-07
source_of_truth: repository
related:
  - "[[docs/how-to/MIGRATE_CONSUMER_MANIFEST]]"
  - "[[docs/architecture/decisions/ADR-0006-versioned-consumer-manifest]]"
  - "[[docs/quality/DEFECTS]]"
---

# Code review A2: consumer manifest migration

## Scope

Проверены planner/apply, fingerprint, Git preconditions, atomic write,
normalization schema 1 → 2, CLI и документация. NPR writer и реальные consumer
manifests не изменялись.

## Findings и решения

1. Первоначальный parser требовал явный `--plan`, хотя safety contract задаёт
   plan-only default. Режим исправлен: отсутствие `--apply` всегда read-only.
2. Проверены stale fingerprint и dirty tree: изменение preimage после review
   блокирует apply до записи.
3. Symlink manifest блокируется; temporary file создаётся рядом с manifest, а
   apply оставляет результат unstaged.
4. Неизвестное legacy `applied` не угадывается и возвращает
   `manual_review_required`.

## Verification

- positive canonical schema 1 и global optout migration;
- outcomes сохраняются побайтно как JSON values;
- mismatch/stale fingerprint, dirty tree и symlink блокируются;
- repeated plan после commit возвращает `up_to_date`;
- full `make check`, strict freshness, `compileall`, `git diff --check`.

## Verdict

Принято для A2. Реальная миграция NPR/BP manifests остаётся отдельной фазой A5.
