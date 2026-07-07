---
id: PC-2026-850607ffdb29
status: accepted
source: "new-project-rules and Best Practices: executable cross-repository contract"
added_by: "Codex по реализованной фазе cross-repo contract"
stack: tools
tags: "contract-test, supply-chain, multi-repo, ci"
applies_to: "governance and tooling dependencies across repositories"
does_not_apply_to: "dependencies already fully represented by package lockfiles or API schemas"
evidence_level: E2
evidence: "NPR PR 4/5 plus BP PR 4/5; reproducible contract tests detect stale routes, missing skills, wrong hashes and ADR drift"
owner: "Best Practices maintainers"
created: 2026-07-07
last_verified: 2026-07-07
review_by: 2027-01-07
supersedes:
superseded_by:
conflicts_with:
candidate: candidates/PC-2026-850607ffdb29-pinned-cross-repo-contract.md
---

# Проверяйте межрепозиторные зависимости закреплённым контрактом

- **Назначение:** обнаруживать несовместимые изменения skills, routes, ADR и разрешённых promotion sources.
- **Вердикт:** Adopt для критичных governance dependencies; Trial для остальных межрепозиторных связей.
- **Настройка:** хранить без секретов repository identity, pinned commit и hashes критичных artifacts; запускать verifier и negative fixtures в CI.
- **Ограничения:** контракт требует явного обновления pin после review и не заменяет API schema или lockfile.
- **Проверка:** fixtures должны падать при missing skill, stale route, wrong hash и несовместимом ADR literal.

## Notes

Pin обновляется только вместе с проверкой diff соседнего repository.
