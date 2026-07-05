---
type: tutorial
status: active
owner: project
last_verified: 2026-07-05
source_of_truth: repository
related:
  - "[[CONTRIBUTING]]"
  - "[[candidates/README]]"
  - "[[docs/reference/PRACTICE_SCHEMA]]"
---

# Первый кандидат за 10 минут

Этот tutorial проводит новый вклад от локального файла до проверенного PR.

## 1. Подготовь evidence

Нужен checked-in артефакт: defect, test, commit, ADR, review или research.
Внешняя статья без проектного подтверждения получает только `E0`.

## 2. Создай файл

Из корня базы выполни:

```sh
python3 scripts/new_candidate.py \
  --slug validate-external-input \
  --title "Валидировать внешний ввод на границе" \
  --stack common \
  --source "sample-project: docs/quality/DEFECTS.md #12" \
  --added-by "developer" \
  --evidence "commit abc123; regression test"
```

Генератор выберет следующий ID и создаст один файл в `candidates/`. При
параллельных PR после rebase проверь уникальность ID через validator.

## 3. Замени placeholders

Заполни все `<заполнить>` конкретными фактами. Удали приватные имена, пути,
хосты и секреты. Объясни границы применимости и почему урок может повториться
не только в исходном проекте.

## 4. Проверь

```sh
make check
```

Команда запускает unit/contract tests, schema validation, проверку ссылок и
эвристики секретов. Исправь все ошибки до PR.

## 5. Открой PR

Один PR содержит одного нового кандидата. Заполни PR template. CODEOWNERS
назначит профильного владельца; первый содержательный ответ ожидается в течение
7 календарных дней.

Кандидат не становится практикой автоматически. Решение принимает
review-workflow; `E1` может стать `trial`, `E2`/`E3` — `accepted`.
