---
type: defect-log
status: active
owner: project
last_verified: 2026-07-07
source_of_truth: repository
related:
  - "[[docs/README]]"
  - "[[INDEX]]"
  - "[[candidates/README]]"
---

# Журнал дефектов

Каждый дефект фиксируется сразу при обнаружении. Статус — по разделу, где лежит
запись: `Open`, `Fixed`, `Won't Fix`. При исправлении запись переносится в
`Fixed` с датой, commit и root cause; записи не удаляются.

## Open

_Нет записей._

## Fixed

### JSON report падал в Windows-консоли с legacy encoding

- **Обнаружено:** 2026-07-14, smoke-test исправления Windows validator
- **Исправлено:** 2026-07-14, текущий commit
- **Root cause:** CLI печатал Unicode JSON через системный `cp1251`; символы из
  practice metadata вне этой кодировки приводили к `UnicodeEncodeError`.
- **Исправление:** `practice_report.py` включает безопасное escaping символов,
  которых нет в активной console encoding; JSON остаётся валидным, а вызывающий
  процесс продолжает декодировать stdout в системной кодировке.

### Windows validator отклонял canonical candidate targets

- **Обнаружено:** 2026-07-14, создание consumer-проекта `favorit-web`
- **Исправлено:** 2026-07-14, текущий commit
- **Root cause:** pair-validation сравнивал POSIX-путь из поля `target` со
  `str(Path.relative_to(...))`; на Windows второй путь содержал обратные слэши,
  поэтому все accepted candidate → practice links считались повреждёнными.
- **Исправление:** repository paths сериализуются через `.as_posix()`, regression
  закрепляет canonical форму, а полный gate выполняется на Windows, Linux и macOS.

### Harvest и apply показывали состав практик только постфактум

- **Обнаружено:** 2026-07-08, поправка пользователя
- **Исправлено:** 2026-07-08, текущий PR
- **Root cause:** skills требовали итоговый отчёт, но не закрепляли обязательный
  preview до создания candidate-файлов или изменения consumer-проекта.
- **Исправление:** harvest/apply обязаны заранее показать ID/название, source,
  evidence, планируемое изменение/outcome и причины пропуска; contract test
  удерживает оба preview gate.

### Сводный pilot report опубликован прямым push через admin bypass

- **Обнаружено:** 2026-07-08, push commit `ce46c47`
- **Исправлено:** 2026-07-08, текущий PR
- **Root cause:** workflow consumer-проектов с прямым push на `main` был
  ошибочно перенесён на BP, где ruleset требует PR и check `validate`.
- **Исправление:** содержимое post-push проверено полным `make check`; нарушение
  зафиксировано, дальнейшие BP changes публикуются только branch → PR → CI → merge.

### NPR writer использовал несовместимые поля consumer manifest

- **Обнаружено:** 2026-07-07, свежий аудит NPR ↔ BP
- **Исправлено:** 2026-07-07, NPR PR №15, merge `5e97b56`; cross-repo gate PR №16,
  merge `c49a0c8`
- **Root cause:** NPR onboarding независимо описывал schema 1 top-level
  `optout` и section `applied`, не исполняя контракт против BP loader.
- **Исправление:** NPR writer/template/docs используют schema 2 `preferences`,
  outcomes пишет BP tooling; real-code E2E работает на трёх ОС.

### CLI migration не запускался после изменения режима по умолчанию

- **Обнаружено:** 2026-07-07, code review A2
- **Исправлено:** 2026-07-07, текущий commit A2
- **Root cause:** при снятии обязательности `--plan` объявление `main()` было
  ошибочно оставлено с лишним отступом, что приводило к `IndentationError` до
  запуска тестов.
- **Исправление:** отступ восстановлен; отдельный CLI test закрепляет read-only
  plan как режим по умолчанию, полный `make check` проходит.

### Intake README сохранял удалённый прямой маршрут meta-уроков в NPR

- **Обнаружено:** 2026-07-07, code review фазы наполнения BP
- **Исправлено:** 2026-07-07, PR №16
- **Root cause:** routing contract test проверял README проекта и skill, но не
  активную инструкцию `candidates/README.md`.
- **Исправление:** intake README направляет meta/process-уроки через BP review;
  active-surface test теперь включает этот файл.

### Harvest skill не называл точные обязательные поля tools/prompts

- **Обнаружено:** 2026-07-07, validation кандидатов tools/prompts
- **Исправлено:** 2026-07-07, PR №16
- **Root cause:** prose описывал смысл полей, а validator проверял точные
  заголовки, не закреплённые contract test.
- **Исправление:** skill перечисляет точные заголовки; repository-contract test
  удерживает синхронизацию.

### Harvest вышел за явно заданную пару проектов

- **Обнаружено:** 2026-07-07
- **Исправлено:** 2026-07-07, PR №7
- **Описание:** при наполнении Best Practices агент использовал evidence из
  `jira-analytics`, хотя пользователь задал анализ и продолжение работ в рамках
  связки `new-project-rules ↔ Best Practices`.
- **Root cause:** требование повысить разнообразие и уровень evidence было
  ошибочно приоритизировано выше явной границы scope.
- **Исправление:** посторонний кандидат удалён; продолжение harvest ограничено
  двумя названными проектами. Перед harvest допустимый список source
  repositories фиксируется явно и не расширяется ради метрик.

### Документация направляла meta/process-уроки в удалённый NPR skill

- **Обнаружено:** 2026-07-07
- **Исправлено:** 2026-07-07, PR №4, merge commit `b259ae9`
- **Root cause:** изменение cross-repository контракта проверялось только в NPR;
  общего compatibility test для активных routing surfaces BP не было.
- **Исправление:** README и canonical harvest skill используют единый маршрут
  через BP review, затем maintainer-only
  `promote-project-knowledge → apply-promotion-candidate`; contract test
  запрещает retired route в active surfaces.

### P1 hardening не был интегрирован в `main`

- **Обнаружено:** 2026-07-07
- **Исправлено:** 2026-07-07, PR №2, merge commit `712e51d`
- **Root cause:** реализация и локальные review завершились без финального
  PR/merge gate, поэтому checked branch и опубликованный продукт разошлись.
- **Исправление:** итоговый diff прошёл полный code review, `make check` и
  GitHub check `validate`; PR №2 объединён в `main`, затем `make check` повторно
  прошёл на merge commit.

### `AGENTS.md` содержал незаполненные шаблонные Commands и Done when

- **Обнаружено:** 2026-07-05
- **Исправлено:** 2026-07-06, commit `70e4318`
- **Root cause:** bootstrap-шаблон не был заменён фактическими командами и
  критериями после появления рабочего `Makefile` и CI gate.
- **Исправление:** раздел `Commands` теперь документирует проверенные targets
  `make`; `Done when` требует успешный `make check`, проверку diff, актуальные
  навигацию и defect log, а также commit и push с учётом remote-approval rules.

### Default consumer report пропускал кросс-разделы практик

- **Обнаружено:** 2026-07-06
- **Исправлено:** 2026-07-06, commit `08b3e8a`
- **Root cause:** CLI моделировал только language stacks, хотя knowledge model
  также содержит cross-cutting категории.
- **Исправление:** default report включает `common`, detected stacks и четыре
  cross-sections; добавлены явный `--section`, совместимые JSON fields и
  end-to-end CLI fixture со всеми семью разделами.

### Secret-проверка не охватывала репозиторий целиком

- **Обнаружено:** 2026-07-06
- **Исправлено:** 2026-07-06, commit `7e32615`
- **Root cause:** secret patterns вызывались как часть schema-validation только
  для candidate/practice, хотя policy распространялась на весь репозиторий.
- **Исправление:** добавлен scan tracked и новых non-ignored текстовых файлов,
  явный reviewed suppression marker и негативные тесты вне `candidates/`.

### Последовательные ID кандидатов конфликтовали между параллельными PR

- **Обнаружено:** 2026-07-06
- **Исправлено:** 2026-07-06, commit `7e32615`
- **Root cause:** локальный `max + 1` ошибочно использовался как глобальный
  allocator в распределённом Git workflow.
- **Исправление:** новые ID используют 48-битный random suffix; legacy ID
  сохранены, локальные совпадения повторно генерируются, решение закреплено в
  [[docs/architecture/decisions/ADR-0004-collision-resistant-candidate-ids]].

### Validator не связывал evidence кандидата и принятой практики

- **Обнаружено:** 2026-07-06
- **Исправлено:** 2026-07-06, commit `7e32615`
- **Root cause:** pair-validation проверял identity/provenance, но пропускал
  поля, определяющие зрелость решения.
- **Исправление:** `evidence` и `evidence_level` обязаны совпадать; отдельные
  negative tests блокируют подмену evidence и одностороннее повышение уровня.

### Skill `harvest-practice-candidates` ссылался на несуществующий ADR

- **Обнаружено:** 2026-07-06
- **Исправлено:** 2026-07-06, commit `7e32615`
- **Root cause:** ADR был переименован без синхронного обновления обязательного
  пути в skill и без contract test.
- **Исправление:** путь исправлен на фактический ADR, наличие обязательного файла
  проверяется repository-contract test.

### Защита `main` описана, но не включена на GitHub

- **Обнаружено:** 2026-07-05
- **Исправлено:** 2026-07-06, GitHub repository ruleset `Protect main`
  (`id: 18538769`; external configuration, без repository commit)
- **Описание:** первоначально `CONTRIBUTING.md` описывал защиту, которой не было.
  На 2026-07-06 активный ruleset для default branch требует pull request,
  один approval, Code Owner review, разрешение review threads и status check
  `validate`, а также запрещает deletion и non-fast-forward updates.
- **Root cause:** governance был задокументирован до применения серверной
  настройки; проверка только legacy branch-protection endpoint недостаточна,
  потому что repository rulesets проверяются отдельным API.

### Одиночная таблица кандидатов давала merge-конфликты при командном приёме

- **Обнаружено:** 2026-07-05
- **Исправлено:** 2026-07-05, commit `09f3a16`
- **Описание:** staging кандидатов был реализован как единая таблица
  `docs/quality/PRACTICE_CANDIDATES.md`. Проект явно рассчитан на командную
  работу через pull request, где несколько контрибьюторов присылают кандидатов
  параллельно. Правки в одну и ту же таблицу гарантированно порождали бы
  merge-конфликты.
- **Root cause:** при проектировании модель совместной работы (много авторов,
  приём через PR) не была спроецирована на конкурентные свойства структуры
  данных. Общий изменяемый агрегат (таблица) выбран там, где нужен
  append-only формат.
- **Исправление:** переход на «файл-на-кандидата» в `candidates/` (один PR —
  один новый файл), плюс `CONTRIBUTING.md` и branch protection.
- **Урок (абстрактно):** если общий артефакт будут править многие через PR,
  проектировать хранение как один-файл-на-элемент, а не как единый изменяемый
  файл/таблицу. Кандидат на promotion в общий стандарт.

## Won't Fix

_Нет записей._
