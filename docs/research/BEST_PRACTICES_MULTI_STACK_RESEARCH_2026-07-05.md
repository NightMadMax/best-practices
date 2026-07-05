---
type: research
status: complete
owner: project
last_verified: 2026-07-05
source_of_truth: repository
related:
  - "[[README]]"
  - "[[PROJECT]]"
  - "[[CONTRIBUTING]]"
  - "[[candidates/README]]"
  - "[[docs/quality/DEFECTS]]"
---

# Консолидация best practices для многих стеков и разработчиков

## Executive summary

Текущая архитектура выбрала правильное ядро: Git как source of truth,
docs-as-code, раздельные import/review/apply, provenance, PR-review и
«один файл — один кандидат». Для текущего размера не нужен Backstage или
отдельная knowledge-платформа: Markdown + Git остаются более дешёвым и
проверяемым решением.

Однако проект пока является **описанием процесса, а не работающей системой**.
Он не обеспечивает заявленные правила автоматически, не моделирует
устаревание и конфликт практик, не распределяет владение по стекам и не даёт
новому разработчику короткого проверяемого golden path. Главный следующий шаг
— не расширять число разделов, а превратить правила в исполнимый контракт:
машиночитаемая схема, validator, CODEOWNERS, PR template, обязательный CI и
жизненный цикл practice-as-code.

## Метод

- Проверены фактическая структура репозитория, три skill-workflow, ADR,
  contribution model, defect log и удалённое состояние GitHub.
- Выводы сопоставлены с первичными/официальными материалами GitHub, Backstage,
  DORA/Google, Thoughtworks, CNCF и Diátaxis.
- Рекомендации разделены на обязательные сейчас и условные при росте.

## Что уже сделано правильно

1. **Docs-as-code и единый source of truth.** Backstage TechDocs также строится
   на хранении документации рядом с кодом и обновлении через обычный PR.
2. **Staging отделён от принятой базы.** Это защищает потребителей от
   непроверенных рекомендаций.
3. **Один кандидат — один файл.** Такой append-friendly формат снижает
   конфликтность параллельных вкладов.
4. **Provenance обязателен.** Источник, автор и evidence препятствуют
   превращению базы в набор анонимных мнений.
5. **Есть явные роли contributor/maintainer и границы scope.** CNCF рекомендует
   документировать mission/scope и минимальные роли contributor, reviewer,
   maintainer.
6. **Tech Radar применяется как решение, а не список инструментов.** Это
   соответствует модели лёгкого технологического governance Thoughtworks.

## Критические разрывы

### P0. Governance описан, но не обеспечивается

GitHub API на 2026-07-05 вернул `Branch not protected`; workflows отсутствуют.
Следовательно, обязательный PR, review и status checks существуют только в
тексте. GitHub прямо связывает protected branches/rulesets с обязательными
review и checks, а CODEOWNERS — с автоматическим назначением профильных
ревьюеров.

**Нужно:** ruleset для `main`, `CODEOWNERS` по разделам, PR template и один
required check `validate`. Удалённую настройку выполнять только после
согласования владельца репозитория.

### P0. Схема кандидата не валидируется

Сейчас YAML-поля и статусы проверяет только человек/агент. Ошибка в `id`,
`target`, `status`, дублирование ID, пустой evidence или секрет попадут в PR без
детерминированного сигнала.

**Нужно:** стандартный validator без тяжёлых зависимостей, проверяющий:

- уникальность `id` и соответствие имени файла;
- допустимые `status`, `stack`, `target` и переходы статусов;
- обязательные `source`, `added_by`, `evidence`, даты и структурные секции;
- существование target, отсутствие приватных путей и очевидных secret patterns;
- wikilinks/локальные ссылки и синхронность индексов.

Одна команда должна одинаково запускаться локально и в CI. Это одновременно
становится реальным разделом `Commands` и критерием `Done when`.

### P1. Принятые практики снова агрегируются в общие README

Intake исправил merge-конфликты через «один файл — один кандидат», но review
добавляет все принятые записи в общие `practices/<stack>/README.md`. При росте
это вернёт ту же конкурентную проблему и усложнит ownership, историю и
депрекацию отдельной практики.

**Нужно:** сохранить стабильный ID и переносить принятую практику в отдельный
файл, например `practices/web/BP-2026-001-<slug>.md`; README раздела оставить
ручным или генерируемым индексом. Один PR по-прежнему должен менять один
логический объект.

### P1. Нет жизненного цикла после принятия

`accepted` сейчас выглядит бессрочным. Но инструменты, версии и рекомендации
устаревают; Open Source Guides советует явно помечать устаревшую документацию,
если её нельзя поддерживать. Поля `last_verified`, owner и replacement должны
быть у самой практики, а не только у индексного README.

**Нужно:** состояния `trial`, `accepted`, `deprecated`, `superseded`,
`rejected`; поля `owner`, `review_by`, `applies_to`, `does_not_apply_to`,
`evidence_level`, `supersedes`, `conflicts_with`. CI должен предупреждать о
просроченном `review_by`, но не блокировать обычный вклад на первом этапе.

### P1. Evidence недостаточно формализован

Требование «полезно минимум двум проектам» есть в skill, но не в схеме и не в
решении о статусе. Одна строка `evidence` не различает мнение, единичный кейс,
эксперимент и повторённый результат.

**Нужно:** простая шкала:

| Уровень | Смысл | Допустимое решение |
|---|---|---|
| E0 | мнение/внешняя ссылка | `new` / `assess` |
| E1 | один проект | `triaged` / `trial` |
| E2 | два независимых проекта или воспроизводимый тест | `accepted` |
| E3 | повторяемая автоматическая проверка + несколько проектов | default/adopt |

Внешний авторитетный источник усиливает объяснение, но не заменяет локальную
проверку применимости.

### P1. Онбординг не является golden path

Новый разработчик должен самостоятельно ответить на пять вопросов: что читать,
как найти свой стек, как предложить практику, как локально проверить PR и когда
ожидать review. Сейчас ответы распределены, а проверочной команды и SLA нет.
DORA связывает качество документации с ясностью, findability и reliability;
Backstage golden paths и templates показывают ценность короткого стандартного
пути с предсказуемым результатом.

**Нужно:** в `CONTRIBUTING.md` добавить 10-минутный сценарий:

1. выбрать тип вклада по decision tree;
2. создать файл одной командой или из шаблона;
3. заполнить один реальный обезличенный пример;
4. запустить `validate`;
5. открыть PR и увидеть владельца, checks и ожидаемый срок ответа.

Документацию полезно разделять по Diátaxis: tutorial для первого вклада,
how-to для harvest/review/apply, reference для схемы, explanation для ADR.

### P2. Таксономия привязана к двум стекам

Каталоги `1c`, `web`, `common` подходят для старта, но плохо масштабируются на
mobile, data, embedded, infrastructure и смешанные проекты. Жёсткое дерево
заставляет дублировать кросс-стековые практики.

**Нужно:** не создавать заранее пустые каталоги. Добавить множественные tags и
dimensions (`language`, `framework`, `runtime`, `domain`, `os`, `lifecycle`),
оставив один канонический файл. Новый stack-раздел появляется только с первым
реальным владельцем и принятой практикой.

### P2. Доставка не оставляет машиночитаемого следа

`apply-best-practices` предлагает ссылаться на источник в правках, но не хранит
manifest применённых ID/версий. Невозможно ответить, какие проекты получили
практику, где она отклонена и повторился ли после применения исходный дефект.

**Нужно:** необязательный `.best-practices.json` в проекте-потребителе с ID,
commit базы, результатом `applied/already-compliant/not-applicable/deferred` и
датой. Сначала — report/diff, изменения только после подтверждения.

## Целевая operating model

```text
project evidence -> candidate file -> automated validation -> stack owner review
       -> trial -> second independent evidence -> accepted practice file
       -> pull/apply report -> consumer manifest -> feedback/new evidence
       -> re-review, supersede or deprecate
```

Роли:

- **Contributor** приносит наблюдение и evidence, не обязан знать всю базу.
- **Triage maintainer** проверяет схему, приватность, дедуп и маршрутизацию.
- **Stack owner** отвечает за техническую корректность и применимость.
- **Cross-stack reviewer** проверяет обобщение и конфликт с общими практиками.
- **Consumer** явно принимает или отклоняет применение в своём проекте.

Для малой команды один человек может совмещать роли, но ответственность должна
быть видна в CODEOWNERS/frontmatter.

## Приоритетный план

### Этап 1 — сделать текущую модель исполнимой

1. Добавить schema validator, fixtures и локальную команду проверки.
2. Добавить GitHub Actions check, PR template и CODEOWNERS.
3. После согласования включить ruleset/branch protection.
4. Заполнить реальные `Commands` и `Done when` в `AGENTS.md` между сессиями.
5. Провести один end-to-end pilot: harvest -> review -> apply на двух проектах.

### Этап 2 — обеспечить масштабирование и доверие

1. Перейти к одному файлу на принятую практику со стабильным ID.
2. Добавить evidence levels, owner, applicability и freshness lifecycle.
3. Описать конфликт, supersede и deprecation отдельным ADR.
4. Ввести consumer manifest и отчёт о неприменённых практиках.

### Этап 3 — улучшить обнаружение, только когда появится спрос

1. Генерировать searchable index/статическую документацию из frontmatter.
2. Рассматривать Backstage/TechDocs, когда десятки репозиториев и команд
   действительно нуждаются в каталоге, владельцах и едином портале.
3. Не вводить портал раньше validator и governance: интерфейс не исправляет
   некачественную модель данных.

## Метрики результата

- median time от первого открытия README до валидного первого PR;
- доля PR, прошедших validator с первого раза;
- median review lead time и число кандидатов без владельца;
- доля practices с актуальным `review_by`;
- число повторных независимых подтверждений на принятую практику;
- adoption/not-applicable rate при `apply`;
- recurrence rate дефектов, которые принятая практика должна предотвращать;
- число конфликтов/superseded записей и время их разрешения.

Vanity metrics (число Markdown-файлов, кандидатов или звёзд) не доказывают, что
практики находят, применяют и что они уменьшают повторение ошибок.

## Итоговый вердикт

Проект концептуально жизнеспособен и не требует смены платформы. Его зрелость —
**prototype/process-defined**: архитектура intake хорошая, но governance,
валидация, ownership, freshness, evidence и feedback loop ещё не замкнуты.
Правильная ближайшая инвестиция — executable governance и один доказанный
end-to-end цикл, а не массовое наполнение практиками из Интернета.

## Источники

- [GitHub: Managing and standardizing pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/managing-and-standardizing-pull-requests)
- [GitHub: About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [GitHub: Managing protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [Backstage: Software Catalog](https://backstage.io/docs/features/software-catalog/)
- [Backstage: Software Templates](https://backstage.io/docs/features/software-templates/)
- [Backstage: Creating and publishing TechDocs](https://backstage.io/docs/features/techdocs/creating-and-publishing)
- [DORA: Documentation quality](https://dora.dev/capabilities/documentation-quality/)
- [Google: The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [Diátaxis documentation framework](https://diataxis.fr/)
- [Thoughtworks: Lightweight technology governance](https://www.thoughtworks.com/insights/articles/lightweight-technology-governance)
- [Thoughtworks: Lightweight Architecture Decision Records](https://www.thoughtworks.com/en-gb/radar/techniques/lightweight-architecture-decision-records)
- [CNCF: Charter — mission, scope, values and principles](https://contribute.cncf.io/maintainers/governance/charter/)
- [CNCF: Governance best practices](https://contribute.cncf.io/projects/best-practices/governance/)
- [Open Source Guides: Best Practices for Maintainers](https://opensource.guide/best-practices/)
