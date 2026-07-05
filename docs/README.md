---
type: index
status: active
owner: project
last_verified: 2026-07-05
source_of_truth: repository
related:
  - "[[INDEX]]"
  - "[[README]]"
---

# Документация Best Practices

Связанный индекс каталога `docs/`. Обновляйте при добавлении, удалении,
перемещении или изменении назначения файла.

## Quality

| Путь | Назначение |
|---|---|
| [[docs/quality/PRACTICE_CANDIDATES]] | Staging-очередь кандидатов на перенос практик из других проектов |

## Architecture

| Путь | Назначение |
|---|---|
| [[docs/architecture/decisions/README]] | Каталог решений (ADR), включая крупные выборы инструментов |

## Конвейер практик

- **Импорт** — `harvest-practice-candidates` собирает из соседних проектов
  уроки, инструменты/MCP, анти-паттерны, промпты и сниппеты в
  [[docs/quality/PRACTICE_CANDIDATES]].
- **Оценка и принятие** — `review-practice-candidates` переносит кандидата в
  `practices/<стек>/`.
- **Доставка** — `apply-best-practices` (pull) отдаёт принятые практики в
  целевые проекты.

Навигация: [[INDEX]], [[README]].
