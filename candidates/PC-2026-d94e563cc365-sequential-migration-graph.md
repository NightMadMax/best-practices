---
id: PC-2026-d94e563cc365
status: accepted
source: "new-project-rules: sequential schema migrations and migration planner tests"
added_by: "Codex по реализованной фазе NPR schema 2"
stack: common
target: practices/common/PC-2026-d94e563cc365-sequential-migration-graph.md
evidence_level: E2
evidence: "NPR PR 6/7; reproducible scripts/test-migration-planner.py covers 0→1→2, missing/ambiguous graph, forged future history and idempotent apply"
created: 2026-07-07
decided: 2026-07-07
---

# Мигрируйте versioned schema только по последовательному графу

- **Контекст:** управляемые файлы и metadata обновляются между версиями стандарта.
- **Проблема:** прямые скачки версий и непроверенная история делают результат неоднозначным и позволяют пропустить обязательное преобразование.
- **Решение:** описывать явные переходы `from_version → to_version`, требовать единственную непрерывную цепочку до target, атомарно планировать всю цепочку и отклонять missing/ambiguous edges и forged future history.

## Notes

Review: принято как `accepted/E2` на основании воспроизводимого adversarial test suite.
