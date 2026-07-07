---
type: intake
status: active
owner: project
last_verified: 2026-07-05
source_of_truth: repository
related:
  - "[[README]]"
  - "[[INDEX]]"
  - "[[CONTRIBUTING]]"
  - "[[docs/architecture/decisions/ADR-0001-provenance-required]]"
---

# Кандидаты (staging)

Очередь предложений на перенос в базу: технические уроки, инструменты/MCP,
анти-паттерны, промпты, сниппеты. **Один кандидат — один файл** в этой папке.
Так несколько пользователей присылают кандидатов параллельно через PR без
merge-конфликтов (в отличие от общей таблицы).

Это staging, а не source of truth исходного проекта — сюда попадает только
нормализованная, очищенная от приватного контекста и секретов выжимка.

Мета- и процессные уроки (правила агента, шаблоны, workflow) также сначала
оформляются BP-кандидатом — обычно в `prompts` или `common`. Только после
обычного review администратор может затвердить вызревшую практику в
`new-project-rules` через maintainer-only маршрут
`promote-project-knowledge → apply-promotion-candidate`.

## Как прислать кандидата

См. [[CONTRIBUTING]]. Кратко: создать файл через `scripts/new_candidate.py`,
получить collision-resistant ID `PC-<год>-<12hex>`, заполнить тело и открыть
PR. [[candidates/_TEMPLATE|_TEMPLATE.md]] служит справочником полей. Мейнтейнер
разбирает кандидата через skill `review-practice-candidates`.

## Статус-модель (поле `status` во frontmatter)

- `new` — предложен, ещё не разобран.
- `triaged` — нормализован, раздел и целевой файл определены.
- `accepted` — практика перенесена в `practices/<раздел>/`; указан commit.
- `rejected` — отклонён; причина в теле файла.

Принятые/отклонённые файлы не удаляются — журнал решений сохраняется (при
разрастании мейнтейнер переносит их в `candidates/archive/`).

## Схема frontmatter кандидата

| Поле | Смысл |
|---|---|
| `id` | Стабильный идентификатор `PC-2026-001` |
| `status` | `new` / `triaged` / `accepted` / `rejected` |
| `source` | Проект и артефакт, откуда пришло (без приватного текста) |
| `added_by` | Кто предложил/подтвердил: пользователь, автор или агент |
| `stack` | Раздел базы: `1c`/`web`/`common`/`tools`/`anti-patterns`/`prompts`/`snippets` |
| `target` | Будущий файл `practices/<раздел>/PC-*.md` с тем же именем |
| `evidence_level` | `E0` / `E1` / `E2` / `E3` по [[docs/architecture/decisions/ADR-0003-one-practice-per-file]] |
| `evidence` | commit/PR/defect/тест |
| `created` | Дата добавления |
| `decided` | Дата accept/reject (пусто, пока `new`/`triaged`) |

`source` и `added_by` **обязательны** — происхождение по
[[docs/architecture/decisions/ADR-0001-provenance-required]]. Секреты, токены и
приватные хосты не записывать.

После принятия файл кандидата остаётся журналом решения, а применяемый source of
truth создаётся по `target`. Его стабильный `id` и имя сохраняются.
