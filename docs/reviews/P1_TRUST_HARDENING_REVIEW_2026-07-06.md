---
type: code-review
status: complete
owner: project
last_verified: 2026-07-06
source_of_truth: commit 7e32615
related:
  - "[[docs/quality/DEFECTS]]"
  - "[[docs/architecture/decisions/ADR-0004-collision-resistant-candidate-ids]]"
  - "[[docs/reference/PRACTICE_SCHEMA]]"
---

# Code review P1 trust hardening — 2026-07-06

## Scope

Проверен commit `7e32615`: collision-resistant candidate ID, связь evidence
candidate/practice, repository-wide secret scan, schema/ADR/workflow и тесты.

## Findings review-прохода

До приёмки найдены и исправлены:

1. Локальная collision-проверка ошибочно оценивала generator object вместо его
   содержимого.
2. Первоначальный 32-битный ID усилен до 48 бит.
3. Имена файлов из `git ls-files -z` переведены на `os.fsdecode` для корректной
   работы с filesystem encoding.
4. Исправлена неточная запись practice-path в schema reference.
5. Добавлен отдельный negative test для расхождения `evidence_level`.

После исправлений блокирующих и неблокирующих замечаний не осталось.

## Verification

- `make check`: 29/29 tests passed; repository validation passed.
- `python3 scripts/validate.py --strict-freshness`: passed.
- `python3 -m compileall -q scripts tests`: passed.
- `git diff --check`: passed.
- Legacy `PC-YYYY-NNN` и новый `PC-YYYY-<12hex>` покрыты тестами.
- Проверены негативные сценарии подмены evidence, повышения evidence level,
  секрета вне candidate и локальной ID-коллизии.

## Verdict

**Принято.** Реализация закрывает четыре зафиксированных дефекта P1/P2 и
сохраняет обратную совместимость. Следующий открытый приоритет — полнота
cross-section consumer report.
