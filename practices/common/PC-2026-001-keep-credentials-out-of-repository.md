---
id: PC-2026-001
status: accepted
source: "jira-analytics: INTEGRATIONS.md; router-watchdog-ops: INTEGRATIONS.md and .gitignore"
added_by: "harvest"
stack: common
tags: "security, credentials, git"
applies_to: "репозитории, интегрирующиеся с API, CLI или внешними сервисами"
does_not_apply_to: "выбор и эксплуатация platform-specific production secret manager"
evidence_level: E2
evidence: "jira-analytics commit bd8dd211; router-watchdog-ops commit 1a199028"
owner: "@NightMadMax"
created: 2026-07-05
last_verified: 2026-07-05
review_by: 2027-01-05
supersedes:
conflicts_with:
candidate: candidates/PC-2026-001-keep-credentials-out-of-repository.md
---

# Хранить credentials вне репозитория

- **Контекст:** проект использует API, CLI или сервисы с credentials.
- **Проблема:** tracked credentials распространяются через историю Git, клоны,
  CI-логи и резервные копии; удаление из текущей версии не очищает историю.
- **Решение:** хранить значения в environment, системном credential store или
  локальном ignored-конфиге. В Git оставлять только placeholders, имена
  переменных и безопасную инструкцию настройки.
- **Проверка:** secret scan и review tracked-файлов не находят реальные
  значения; приложение получает credential из документированного внешнего
  источника; пример конфигурации работает после подстановки placeholder.

## Notes

Практика не выбирает конкретный production secret manager. Если credential уже
попал в Git, одного удаления недостаточно: требуется ротация и отдельное
решение по очистке истории.
