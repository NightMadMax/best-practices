# Индекс проекта Best Practices

Обновляйте таблицу при добавлении, удалении, перемещении или изменении
назначения файла.

| Путь | Назначение |
|---|---|
| [[README]] | Описание и быстрый старт |
| [[AGENTS]] | Правила агента и workflow |
| [[CLAUDE|CLAUDE.md]] | Imports [[AGENTS]] for Claude Code |
| [[INDEX]] | Карта фактически существующих файлов |
| [[PROJECT]] | Цели, scope, ограничения и критерии успеха |
| [[CONTRIBUTING]] | Как присылать кандидатов через PR |
| [[candidates/README]] | Staging: файлы-кандидаты (один файл — один кандидат) |
| [[candidates/_TEMPLATE]] | Шаблон файла-кандидата |
| [[practices/README]] | Правила и навигация по принятым практикам |
| [[practices/_TEMPLATE]] | Шаблон отдельного файла принятой практики |
| [[practices/1c/README]] | Практики разработки для 1С |
| [[practices/web/README]] | Практики веб-разработки |
| [[practices/common/README]] | Общие практики |
| [[practices/tools/README]] | Инструменты и MCP-серверы (tech-radar) |
| [[practices/anti-patterns/README]] | Анти-паттерны: чего избегать |
| [[practices/prompts/README]] | Промпты и skill-паттерны |
| [[practices/snippets/README]] | Сниппеты и конфиги |
| [[docs/README]] | Индекс каталога `docs/` |
| [[docs/quality/DEFECTS]] | Журнал дефектов проекта |
| [[docs/research/BEST_PRACTICES_MULTI_STACK_RESEARCH_2026-07-05]] | Исследование multi-stack консолидации и онбординга |
| [[docs/research/END_TO_END_PILOT_2026-07-05]] | End-to-end pilot конвейера практик |
| [[docs/research/AGENTS_UPDATE_PROPOSAL_2026-07-05]] | Предложение Commands и Done when для следующей сессии |
| [[docs/reviews/FULL_CODE_REVIEW_2026-07-06]] | Полный code review, harvest-анализ и оценка зрелости |
| [[docs/reviews/P1_TRUST_HARDENING_REVIEW_2026-07-06]] | Review реализации P1 trust hardening |
| [[docs/reviews/CROSS_SECTION_REPORT_REVIEW_2026-07-06]] | Review полноты cross-section consumer report |
| [[docs/reviews/LIFECYCLE_INVARIANTS_REVIEW_2026-07-06]] | Review lifecycle, chronology и supersession invariants |
| [[docs/tutorials/FIRST_CONTRIBUTION]] | Tutorial первого вклада |
| [[docs/how-to/HARVEST_REVIEW_APPLY]] | How-to полного конвейера практики |
| [[docs/reference/PRACTICE_SCHEMA]] | Reference схемы данных и manifest |
| [[docs/architecture/decisions/README]] | Каталог решений (ADR) |
| [[docs/architecture/decisions/ADR-0001-provenance-required]] | Происхождение обязательно для каждой записи |
| [[docs/architecture/decisions/ADR-0002-tool-verdicts-tech-radar]] | Вердикты инструментов по tech-radar |
| [[docs/architecture/decisions/ADR-0003-one-practice-per-file]] | Одна практика — один файл, lifecycle и evidence levels |
| [[docs/architecture/decisions/ADR-0004-collision-resistant-candidate-ids]] | Collision-resistant candidate ID без общего счётчика |
| [[docs/architecture/decisions/ADR-0005-practice-lifecycle-invariants]] | Lifecycle, chronology и replacement invariants практик |

## Скилы конвейера

| Путь | Назначение |
|---|---|
| `.agents/skills/harvest-practice-candidates/` | Импорт уроков из соседних проектов в `candidates/` |
| `.agents/skills/review-practice-candidates/` | Оценка и принятие кандидатов в `practices/` |
| `.agents/skills/apply-best-practices/` | Pull-доставка практик в целевой проект |

Указатели для Claude Code — в `.claude/skills/<name>/SKILL.md`; канон — в
`.agents/skills/<name>/SKILL.md`.
