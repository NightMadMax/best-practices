---
type: how-to
status: active
owner: project
last_verified: 2026-07-05
source_of_truth: repository
related:
  - "[[README]]"
  - "[[docs/tutorials/FIRST_CONTRIBUTION]]"
  - "[[docs/reference/PRACTICE_SCHEMA]]"
---

# Как провести практику через полный конвейер

## Harvest

1. Собери checked-in evidence из исходного проекта.
2. Запусти `harvest-practice-candidates` или создай файл через
   `scripts/new_candidate.py`.
3. Нормализуй приватный контекст и запусти `make check`.

Harvest меняет только `candidates/`, никогда `practices/`.

## Review

1. Проверь дубль, применимость, provenance и evidence level.
2. При accept создай файл по `target` из `practices/_TEMPLATE.md`.
3. Сохрани ID и basename кандидата.
4. `E1` создаёт `trial`; `E2`/`E3` — `accepted`.
5. Обнови индекс стека, статус/дату кандидата и запусти `make check`.

## Apply

Сначала сформируй read-only отчёт:

```sh
python3 scripts/practice_report.py --project /path/to/consumer
```

Trial-практики скрыты по умолчанию. Для осознанной оценки добавь
`--include-trial`. После проверки diff и фактического применения явно запиши
результат:

```sh
python3 scripts/practice_report.py \
  --project /path/to/consumer \
  --record PC-2026-001=applied \
  --notes "tests passed"
```

Допустимые outcomes: `applied`, `already-compliant`, `not-applicable`,
`deferred`. Только `--record` изменяет проект-потребитель.
