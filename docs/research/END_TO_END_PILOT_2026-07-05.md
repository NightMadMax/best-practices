---
type: research
status: complete
owner: project
last_verified: 2026-07-05
source_of_truth: repository
related:
  - "[[docs/how-to/HARVEST_REVIEW_APPLY]]"
  - "[[candidates/PC-2026-001-keep-credentials-out-of-repository]]"
  - "[[practices/common/PC-2026-001-keep-credentials-out-of-repository]]"
---

# End-to-end pilot конвейера практик

## Цель

Проверить полный путь на реальном техническом уроке: два независимых source
project → candidate → review → accepted practice → consumer report → manifest.

## Evidence

- `jira-analytics`, `INTEGRATIONS.md`, commit `bd8dd211`: credentials поступают
  извне репозитория через environment.
- `router-watchdog-ops`, `INTEGRATIONS.md` и `.gitignore`, commit `1a199028`:
  реальные credentials остаются в локальных untracked-конфигах.

Приватные hostname, email и значения credentials в базу не переносились.

## Результат

1. `scripts/new_candidate.py` создал
   [[candidates/PC-2026-001-keep-credentials-out-of-repository]].
2. После нормализации candidate прошёл `make check` в статусе `triaged`/`E2`.
3. Review создал отдельную
   [[practices/common/PC-2026-001-keep-credentials-out-of-repository]] в статусе
   `accepted`; validator подтвердил совпадение ID, provenance, target и
   evidence threshold.
4. Изменение зафиксировано commit `e64dc7a`.
5. На изолированном consumer-проекте первый `practice_report.py` был read-only:
   manifest отсутствовал, outcome был `not-recorded`.
6. Явный `--record PC-2026-001=already-compliant` создал schema-1 manifest с
   полным source commit `e64dc7a87e931783756c0f08ffbe80d22048bfb3`.
7. Повторный отчёт показал `already-compliant`; временный consumer удалён.

## Дефекты, найденные pilot

- Frontmatter-parser не декодировал JSON-escaped строки из generator. Исправлен
  и покрыт regression test.
- До коммита manifest мог сослаться на HEAD без новой practice. Добавлен guard:
  `--record` разрешён только когда practice существует в HEAD и совпадает с
  рабочей копией.
- Статус `accepted` кандидата ошибочно смешивался со зрелостью `accepted`
  практики. Теперь candidate accept допускает E1/trial, а mature practice
  требует E2+.

## Вердикт

Минимальный конвейер замкнут и воспроизводим. Локальная definition of done:
`make check` и `python3 scripts/validate.py --strict-freshness` проходят.
