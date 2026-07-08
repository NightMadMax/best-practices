---
type: research
status: complete
owner: project
last_verified: 2026-07-08
source_of_truth: consumer manifests
related:
  - "[[docs/reference/PRACTICE_METRICS]]"
  - "[[docs/architecture/decisions/ADR-0006-versioned-consumer-manifest]]"
---

# Внешний consumer pilot — 2026-07-08

Проверены `jira-analytics` и `router-watchdog-ops` против BP commit
`e255b6474002ec3a5c4ff16935a24229e9ebf614`.

| Metric | Value |
|---|---:|
| Consumers / manifests | 2 / 2 |
| Recorded decisions | 6 |
| `applied` | 1 |
| `already-compliant` | 3 |
| `not-applicable` | 2 |
| Adoption rate | 66.7% |

Практика последовательных migrations выявила schema-1 drift в router-проекте;
reviewed fingerprinted migration `0004` обновила metadata до schema 2.
Изменений на живых роутерах не выполнялось.

База полезна как проверяемый контрольный слой: четыре из шести решений
подтвердили или улучшили соответствие. Pinned cross-repo contract обоснованно
не применён к consumers без прямой runtime/CI зависимости от BP/NPR.

Следующий этап должен расширять каталог доказанно применимых практик, а не
усложнять инфраструктуру consumer manifest.
