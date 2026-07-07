---
id: PC-2026-850607ffdb29
status: accepted
source: "new-project-rules and Best Practices: executable cross-repository contract"
added_by: "Codex по реализованной фазе cross-repo contract"
stack: tools
target: practices/tools/PC-2026-850607ffdb29-pinned-cross-repo-contract.md
evidence_level: E2
evidence: "NPR PR 4/5 plus BP PR 4/5; reproducible contract tests detect stale routes, missing skills, wrong hashes and ADR drift"
created: 2026-07-07
decided: 2026-07-07
---

# Проверяйте межрепозиторные зависимости закреплённым контрактом

- **Назначение:** обнаруживать несовместимые изменения маршрутов, skills, ADR и разрешённых источников между независимо выпускаемыми репозиториями.
- **Вердикт:** Trial — использовать там, где один repository зависит от конкретных governance artifacts другого.
- **Настройка:** без секретов хранить manifest с repository identity, pinned commit и hashes критичных файлов; verifier читает локальный checkout или явно заданный путь и запускается в CI на поддерживаемых ОС.

## Notes

Контракт не заменяет API compatibility или package manager lockfile. Review: принято как `accepted/E2` по двум repositories и воспроизводимым negative tests.
