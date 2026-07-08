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
| [[docs/architecture/decisions/ADR-0004-collision-resistant-candidate-ids]] | Collision-resistant ID для независимых PR |
| [[docs/architecture/decisions/ADR-0005-practice-lifecycle-invariants]] | Lifecycle, chronology и replacement invariants |
| [[docs/architecture/decisions/ADR-0006-versioned-consumer-manifest]] | Versioned consumer preferences и per-practice outcomes |

## Research

| Путь | Назначение |
|---|---|
| [[docs/research/BEST_PRACTICES_MULTI_STACK_RESEARCH_2026-07-05]] | Исследование консолидации практик многих стеков и онбординга контрибьюторов |
| [[docs/research/END_TO_END_PILOT_2026-07-05]] | Результат полного pilot harvest-review-apply |
| [[docs/research/AGENTS_UPDATE_PROPOSAL_2026-07-05]] | Подготовленное обновление AGENTS.md для следующей сессии |
| [[docs/research/MODERNIZATION_PILOT_2026-07-06]] | Расширенный pilot трёх consumer snapshots и metrics |
| [[docs/research/EXTERNAL_CONSUMER_PILOT_2026-07-08]] | Два внешних consumer pilot и aggregate adoption metrics |

## Reviews

| Путь | Назначение |
|---|---|
| [[docs/reviews/FULL_CODE_REVIEW_2026-07-06]] | Полный code review, harvest-анализ и оценка зрелости |
| [[docs/reviews/P1_TRUST_HARDENING_REVIEW_2026-07-06]] | Review реализации P1 trust hardening |
| [[docs/reviews/CROSS_SECTION_REPORT_REVIEW_2026-07-06]] | Review полноты cross-section consumer report |
| [[docs/reviews/LIFECYCLE_INVARIANTS_REVIEW_2026-07-06]] | Review lifecycle, chronology и supersession invariants |
| [[docs/reviews/METRICS_AND_PILOT_REVIEW_2026-07-06]] | Review metrics CLI и modernization pilot |
| [[docs/reviews/PRACTICE_CATALOG_REVIEW_2026-07-06]] | Review searchable practice catalog |
| [[docs/reviews/PHASE_1_FINAL_REVIEW_2026-07-07]] | Финальный review фазы 1: P1 trust hardening delivery |
| [[docs/reviews/PHASE_3_ROUTING_REVIEW_2026-07-07]] | Review фазы 3: пользовательский knowledge route BP → NPR |
| [[docs/reviews/A2_CONSUMER_MANIFEST_MIGRATION_REVIEW_2026-07-07]] | Code review consumer manifest migration |
| [[docs/reviews/A5_BP_CONSUMER_MANIFEST_MIGRATION_REVIEW_2026-07-07]] | Review фактической миграции BP consumer manifest |

## Tutorials, how-to and reference

| Путь | Назначение |
|---|---|
| [[docs/tutorials/FIRST_CONTRIBUTION]] | Первый валидный кандидат за 10 минут |
| [[docs/how-to/HARVEST_REVIEW_APPLY]] | Полный операционный конвейер практики |
| [[docs/how-to/MIGRATE_CONSUMER_MANIFEST]] | Plan/apply migration consumer manifest schema 1 → 2 |
| [[docs/reference/PRACTICE_SCHEMA]] | Схема кандидата, практики и consumer manifest |
| [[docs/reference/PRACTICE_METRICS]] | Метрики lifecycle, evidence, freshness и consumer outcomes |
| [[docs/reference/PRACTICE_CATALOG]] | Поиск практик по section, status, tag и тексту |

## Конвейер практик

- **Импорт** — `harvest-practice-candidates` собирает из соседних проектов
  уроки, инструменты/MCP, анти-паттерны, промпты и сниппеты в файлы
  [[candidates/README|candidates/]].
- **Оценка и принятие** — `review-practice-candidates` переносит кандидата в
  `practices/<раздел>/`.
- **Доставка** — `apply-best-practices` (pull) отдаёт принятые практики в
  целевые проекты.

Навигация: [[INDEX]], [[README]].
