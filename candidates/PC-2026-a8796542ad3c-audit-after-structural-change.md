---
id: PC-2026-a8796542ad3c
status: accepted
source: "new-project-rules phase 4 review and Best Practices routing defect"
added_by: "Codex с учётом подтверждённого пользователем PLAYBOOK-паттерна"
stack: prompts
target: practices/prompts/PC-2026-a8796542ad3c-audit-after-structural-change.md
evidence_level: E1
evidence: "NPR phase 4 found cross-repo drift; BP PR 4/5 removed stale route and added contract regression"
created: 2026-07-07
decided: 2026-07-07
---

# После структурного изменения запускайте широкий read-only аудит

- **Когда применять:** после изменения архитектуры репозиториев, knowledge route, ADR, skills или GitHub governance.
- **Промпт / паттерн:** «Выполни post-change read-only gate: найди stale routes во всех связанных репозиториях; проверь GitHub rules, открытые PR и remote branches; сопоставь реализацию с ADR consequences; найденные дефекты запиши до следующей фазы».
- **Почему работает:** локальные тесты изменённого компонента не видят устаревшие внешние ссылки и серверное состояние; отдельный широкий gate явно расширяет проверяемую поверхность.

## Notes

Review: принято как `trial/E1`; evidence относится к одной связанной NPR/BP программе.
