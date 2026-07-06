---
type: defect-log
status: active
owner: project
last_verified: 2026-07-06
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

_Нет открытых дефектов._

## Fixed

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
