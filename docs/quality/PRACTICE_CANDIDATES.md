---
type: quality-backlog
status: active
owner: project
last_verified: 2026-07-05
source_of_truth: repository
related:
  - "[[README]]"
  - "[[INDEX]]"
  - "[[docs/README]]"
---

# Practice Candidates

Очередь кандидатов на перенос технических уроков из других проектов в базу
`Best Practices` (`practices/1c`, `practices/web`, `practices/common`).

Этот журнал — **staging**, а не source of truth исходного проекта. Он не
заменяет его `DEFECTS`, `PLAYBOOK`, ADR, research или runbook и хранит только
нормализованные, очищенные от приватного контекста кандидаты.

Здесь живут только **технические/стек-уроки**. Мета- и процессные уроки (про
правила агента, шаблоны, workflow) сюда не попадают — их маршрут ведёт в
стандарт `new-project-rules` через его `promote-project-knowledge`.

## Status model

- `new` — кандидат найден, но ещё не разобран.
- `triaged` — кандидат нормализован, стек и целевой файл определены.
- `accepted` — практика перенесена в `practices/<стек>/`; указан commit.
- `rejected` — перенос отклонён; причина зафиксирована в Notes.

## Entry format

| ID | Status | Source | Added by | Context | Problem | Solution | Stack | Evidence | Target file | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| _пример_ PC-2026-001 | triaged | `Роутеры и Watchdog`: [[docs/quality/DEFECTS]] `#12` | Max | Когда применимо | Что шло не так | Как делать правильно | `1c` \| `web` \| `common` \| `tools` … | defect/PR/тест/commit | `practices/1c/README.md` | Причина статуса, дубли, follow-up |

### Field guide

- **ID** — стабильный идентификатор, например `PC-2026-001`.
- **Status** — одно из значений status model.
- **Source** — проект и исходный артефакт, без копирования приватного текста.
- **Added by** — кто предложил/подтвердил кандидата: пользователь (имя/роль),
  автор коммита или агент, если найдено автоматически (обязательно, см.
  [[docs/architecture/decisions/ADR-0001-provenance-required]]).
- **Context** — когда практика применима (поле формата практики).
- **Problem** — наблюдаемая проблема из источника.
- **Solution** — обобщённое правильное решение.
- **Stack** — целевой раздел базы: стек `1c`/`web`/`common` или кросс-раздел
  `tools`/`anti-patterns`/`prompts`/`snippets`.
- **Evidence** — defect, test, research, commit, PR или воспроизводимый опыт.
- **Target file** — конкретный файл в `practices/<стек>/`.
- **Notes** — причина accept/reject, дубли, ограничения, follow-up.

## Workflow

1. `harvest-practice-candidates` находит и добавляет/обновляет кандидатов со
   статусом `new` или `triaged`; `practices/` напрямую не трогает.
2. `review-practice-candidates` переводит кандидата в `accepted` (с переносом в
   `practices/<стек>/`) или `rejected` (с причиной).
3. `apply-best-practices` доставляет уже принятые практики в целевые проекты
   (pull), из этого журнала не читает.

## Rules

- Заполнять `Source` и `Added by` у каждого кандидата: запись без происхождения
  к review не допускается.
- Не создавать дубли: при похожем кандидате обновлять существующую запись.
- Не выставлять `accepted` автоматически без явной просьбы или отдельного review.
- Хранить строку кандидата и после `accepted`/`rejected` — журнал не чистится.
- Убирать секреты, персональные данные и machine-specific paths до записи.
