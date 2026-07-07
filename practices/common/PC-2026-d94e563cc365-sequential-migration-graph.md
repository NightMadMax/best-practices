---
id: PC-2026-d94e563cc365
status: accepted
source: "new-project-rules: sequential schema migrations and migration planner tests"
added_by: "Codex по реализованной фазе NPR schema 2"
stack: common
tags: "migration, schema, graph, idempotency"
applies_to: "versioned managed configuration and metadata"
does_not_apply_to: "unversioned disposable data without upgrade compatibility"
evidence_level: E2
evidence: "NPR PR 6/7; reproducible scripts/test-migration-planner.py covers 0→1→2, missing/ambiguous graph, forged future history and idempotent apply"
owner: "Best Practices maintainers"
created: 2026-07-07
last_verified: 2026-07-07
review_by: 2027-01-07
supersedes:
superseded_by:
conflicts_with:
candidate: candidates/PC-2026-d94e563cc365-sequential-migration-graph.md
---

# Мигрируйте versioned schema только по последовательному графу

- **Контекст:** управляемые файлы и metadata обновляются между версиями.
- **Проблема:** прямые скачки и непроверенная history пропускают обязательные преобразования.
- **Решение:** задавать явные `from → to` edges, требовать единственную непрерывную цепочку и атомарно применять весь план.
- **Проверка:** negative tests отклоняют missing/ambiguous edges и forged future history; повторный apply идемпотентен.

## Notes

Невыполненный edge является ошибкой контракта, а не поводом угадывать путь.
