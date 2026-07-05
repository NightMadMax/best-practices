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
| [[docs/quality/DEFECTS]] | Журнал дефектов проекта (Open / Fixed / Won't Fix) |

Staging-очередь кандидатов вынесена в корень репозитория —
[[candidates/README|candidates/]] (файл на кандидата, приём через PR).

## Architecture

| Путь | Назначение |
|---|---|
| [[docs/architecture/decisions/README]] | Каталог решений (ADR), включая крупные выборы инструментов |
| [[docs/architecture/decisions/ADR-0003-one-practice-per-file]] | Формат отдельной практики, lifecycle и evidence levels |

## Research

| Путь | Назначение |
|---|---|
| [[docs/research/BEST_PRACTICES_MULTI_STACK_RESEARCH_2026-07-05]] | Исследование консолидации практик многих стеков и онбординга контрибьюторов |

## Tutorials, how-to and reference

| Путь | Назначение |
|---|---|
| [[docs/tutorials/FIRST_CONTRIBUTION]] | Первый валидный кандидат за 10 минут |
| [[docs/how-to/HARVEST_REVIEW_APPLY]] | Полный операционный конвейер практики |
| [[docs/reference/PRACTICE_SCHEMA]] | Схема кандидата, практики и consumer manifest |

## Конвейер практик

- **Импорт** — `harvest-practice-candidates` собирает из соседних проектов
  уроки, инструменты/MCP, анти-паттерны, промпты и сниппеты в файлы
  [[candidates/README|candidates/]].
- **Оценка и принятие** — `review-practice-candidates` переносит кандидата в
  `practices/<раздел>/`.
- **Доставка** — `apply-best-practices` (pull) отдаёт принятые практики в
  целевые проекты.

Навигация: [[INDEX]], [[README]].
