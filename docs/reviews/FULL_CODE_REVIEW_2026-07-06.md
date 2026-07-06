---
type: code-review
status: complete
owner: project
last_verified: 2026-07-06
source_of_truth: repository
related:
  - "[[docs/quality/DEFECTS]]"
  - "[[docs/research/END_TO_END_PILOT_2026-07-05]]"
  - "[[docs/reference/PRACTICE_SCHEMA]]"
---

# Полный code review и harvest-анализ — 2026-07-06

## Scope и метод

Аудит выполнен с нуля по текущему `main` (`d842762`): прочитаны код, тесты,
skills, workflow, ADR, schema, candidate/practice pair, документация и история.
Проверены локальные команды и текущее состояние GitHub repository governance.
Исправления реализации не выполнялись; найденные дефекты записаны в
[[docs/quality/DEFECTS]].

## Findings

### P1 — последовательные candidate ID конфликтуют между параллельными PR

`scripts/new_candidate.py` выбирает `max(existing) + 1` из локального checkout.
Два независимых автора от одного `main` получают одинаковый ID. После merge
первого PR второй становится невалидным, хотя file-per-candidate архитектура
заявлена именно как средство независимого параллельного вклада.

**Evidence:** два независимых временных состояния с `PC-2026-001` оба вернули
`PC-2026-002`.

### P1 — evidence кандидата и practice не образует защищённую цепочку

Pair-validator сравнивает `id`, `source`, `added_by` и `stack`, но не сравнивает
`evidence` и `evidence_level`. Practice можно локально повысить с E1 до E2 и
получить mature `accepted`, не изменив candidate journal; validator возвращает
пустой список проблем. Это нарушает центральную trust-модель проекта.

### P1 — repository-wide запрет секретов не исполняется

Secret patterns запускаются только для candidate/practice файлов. Секрет в
README, skill, script, test или другой tracked-документации проходит
`make check`. PR template обещает более широкий контракт, чем обеспечивает CI.

### P1 — default apply-report будет неполным после роста базы

`practice_report.py` автоматически включает только `common`, `web` и `1c`,
тогда как apply-skill требует учитывать `tools`, `anti-patterns`, `prompts` и
`snippets`. Сейчас это скрыто пустыми разделами; после их наполнения golden path
начнёт молча пропускать принятые записи.

### P2 — harvest-skill содержит stale обязательный путь

Skill требует `ADR-0003-candidate-staging-model.md`, но реальный файл —
`ADR-0003-one-practice-per-file.md`. Локальные contract tests проверяют только
metadata Claude pointers, но не существование путей, указанных внутри skills.

### P2 — активный AGENTS.md не содержит фактический definition of done

Разделы `Commands` и `Done when` остаются bootstrap-подсказками, хотя реальные
команды уже существуют. Готовое предложение лежит в
[[docs/research/AGENTS_UPDATE_PROPOSAL_2026-07-05]], но пока не применено.

## Что подтверждено как сильная сторона

- Чётко разделены harvest, review и apply; staging не смешан с принятой базой.
- Schema и lifecycle описаны в ADR и исполняются validator в основных happy и
  negative paths.
- Код на Python standard library компактен и переносим; внешних runtime
  зависимостей нет.
- GitHub Actions использует read-only permissions и actions, закреплённые по
  полному commit SHA.
- Активный ruleset default branch требует PR, approval, Code Owner review,
  разрешение threads и check `validate`; последние CI runs успешны.
- End-to-end pilot реально прошёл candidate → practice → consumer manifest.
- Документация хорошо разложена по tutorial/how-to/reference/ADR и связана
  wikilinks.

## Проверки

- `make check` — 22/22 tests passed; validator passed.
- `python3 scripts/validate.py --strict-freshness` — passed.
- `python3 -m compileall -q scripts tests` — passed.
- CLI smoke (`--help`) — passed.
- `git diff --check` — passed до оформления отчёта.
- GitHub: `main` синхронен с `origin/main`; open PR нет; только branch `main`;
  последние три Validate runs успешны.

## Harvest result

Новых `candidates/PC-*.md` не создано. Единственный доказанный технический урок
этого репозитория уже представлен как `PC-2026-001`. Остальные найденные
сигналы относятся к реализации и governance самого knowledge pipeline либо к
мета-процессу стандартов; без второго независимого project evidence они не
проходят фильтр кросс-проектной практики. Fixed-урок про file-per-item следует
рассматривать для `new-project-rules`, а не принимать в technical practices.

## Оценка зрелости

**Уровень: ранняя beta / process-defined, 2.5 из 5.**

Проект уже выше prototype: есть исполнимый validator, CI, governance, ADR,
тесты и один полный pilot. Но он ещё не production-mature knowledge system:
корпус состоит из одной принятой практики, trust-chain evidence имеет обход,
contributor concurrency не решена, cross-section delivery не доказана, а
метрики adoption/recurrence пока не накоплены.

Следующий критерий зрелости — не число Markdown-файлов, а закрытие P1-инвариантов
и минимум несколько независимых циклов harvest → review → apply с измеримым
consumer outcome.
