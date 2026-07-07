---
id: PC-2026-a8796542ad3c
status: trial
source: "new-project-rules phase 4 review and Best Practices routing defect"
added_by: "Codex с учётом подтверждённого пользователем PLAYBOOK-паттерна"
stack: prompts
tags: "agent, audit, governance, multi-repo"
applies_to: "structural, governance and cross-repository changes"
does_not_apply_to: "isolated content edits without external dependencies"
evidence_level: E1
evidence: "NPR phase 4 found cross-repo drift; BP PR 4/5 removed stale route and added contract regression"
owner: "Best Practices maintainers"
created: 2026-07-07
last_verified: 2026-07-07
review_by: 2026-10-07
supersedes:
superseded_by:
conflicts_with:
candidate: candidates/PC-2026-a8796542ad3c-audit-after-structural-change.md
---

# После структурного изменения запускайте широкий read-only аудит

- **Когда применять:** после изменения architecture, knowledge routes, ADR, skills или GitHub governance.
- **Промпт / паттерн:** «Выполни post-change read-only gate: найди stale routes во всех связанных repositories; проверь GitHub rules, PR и remote branches; сопоставь реализацию с ADR consequences; запиши defects до следующей фазы».
- **Почему работает:** локальные tests не видят устаревшие внешние ссылки и server-side state; gate явно расширяет проверяемую поверхность.
- **Проверка:** отчёт содержит результаты каждого пункта и ссылки на записанные defects либо явное `не найдено`.

## Notes

Trial до независимого повторного подтверждения за пределами NPR/BP программы.
