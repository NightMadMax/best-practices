---
id: PC-2026-850607ffdb29
status: triaged
source: "new-project-rules and Best Practices: executable cross-repository contract"
added_by: "Codex по реализованной фазе cross-repo contract"
stack: tools
target: practices/tools/PC-2026-850607ffdb29-pinned-cross-repo-contract.md
evidence_level: E1
evidence: "NPR PR 4/5 plus BP PR 4/5: pinned commit/hash contract detects stale routes, missing skills and ADR drift in CI"
created: 2026-07-07
decided:
---

# Проверяйте межрепозиторные зависимости закреплённым контрактом

- **Назначение:** обнаруживать несовместимые изменения маршрутов, skills, ADR и разрешённых источников между независимо выпускаемыми репозиториями.
- **Вердикт:** Trial — использовать там, где один repository зависит от конкретных governance artifacts другого.
- **Настройка:** без секретов хранить manifest с repository identity, pinned commit и hashes критичных файлов; verifier читает локальный checkout или явно заданный путь и запускается в CI на поддерживаемых ОС.

## Notes

Контракт не заменяет API compatibility или package manager lockfile. Harvest оставляет E1; автоматические negative tests будут оценены review-этапом.
