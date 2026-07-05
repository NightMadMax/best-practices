---
id: PC-2026-001
status: accepted
source: "jira-analytics: INTEGRATIONS.md; router-watchdog-ops: INTEGRATIONS.md and .gitignore"
added_by: "harvest"
stack: common
target: practices/common/PC-2026-001-keep-credentials-out-of-repository.md
evidence_level: E2
evidence: "jira-analytics commit bd8dd211; router-watchdog-ops commit 1a199028"
created: 2026-07-05
decided: 2026-07-05
---

# Хранить credentials вне репозитория

- **Контекст:** проект использует API, CLI или сервисы с credentials.
- **Проблема:** credentials в tracked-файлах и примерах попадают в историю Git,
  копии репозитория и логи автоматизации; простого удаления недостаточно.
- **Решение:** хранить значения в environment, системном credential store или
  локальном ignored-конфиге; коммитить только placeholders и способ настройки.

## Notes

Подтверждено двумя независимыми проектами и применимо к любому репозиторию с
аутентификацией. Не описывает runtime secret manager для production — его выбор
зависит от платформы.

Решение: принято как `accepted`/`E2` в ходе end-to-end pilot 2026-07-05;
commit будет зафиксирован историей Git этого изменения.
