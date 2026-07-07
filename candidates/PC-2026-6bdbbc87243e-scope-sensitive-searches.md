---
id: PC-2026-6bdbbc87243e
status: new
source: "jira-analytics: docs/operations/agent-defect-log.md D-004"
added_by: "Codex, по подтверждённому дефекту проекта"
stack: common
target: practices/common/PC-2026-6bdbbc87243e-scope-sensitive-searches.md
evidence_level: E1
evidence: "jira-analytics D-004: широкий поиск раскрыл credential из backup/state/session; исправлен whitelist активных файлов"
created: 2026-07-07
decided:
---

# Ограничивайте поиск потенциально чувствительных настроек

- **Контекст:** диагностика пользовательских профилей, интеграций и локальных конфигураций.
- **Проблема:** рекурсивный поиск по profile, backup, state, sessions и logs может вывести исторические credentials в журнал агента или CI.
- **Решение:** сначала задавать whitelist активных файлов и каталогов, исключать state/backup/session/log surfaces и санитизировать потенциально чувствительный вывод до отображения.

## Notes

Кандидат не разрешает читать секреты и не содержит их значений. Evidence пока относится к одному проекту, поэтому максимальный результат review — `trial`.
