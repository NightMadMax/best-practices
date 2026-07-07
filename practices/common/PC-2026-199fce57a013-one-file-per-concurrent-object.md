---
id: PC-2026-199fce57a013
status: trial
source: "Best Practices: docs/quality/DEFECTS.md, общий staging кандидатов"
added_by: "Codex по подтверждённому дефекту BP"
stack: common
tags: "git, collaboration, pull-request, storage"
applies_to: "append-only каталоги и независимо создаваемые записи"
does_not_apply_to: "малые атомарные документы с единым владельцем"
evidence_level: E1
evidence: "BP defect: общая таблица кандидатов вызывала merge conflicts; исправлено переходом на file-per-object"
owner: "Best Practices maintainers"
created: 2026-07-07
last_verified: 2026-07-07
review_by: 2026-10-07
supersedes:
superseded_by:
conflicts_with:
candidate: candidates/PC-2026-199fce57a013-one-file-per-concurrent-object.md
---

# Храните независимо изменяемые объекты в отдельных файлах

- **Контекст:** несколько участников создают однотипные записи через независимые pull request.
- **Проблема:** единая таблица превращает несвязанные изменения в конфликтующие правки одного файла.
- **Решение:** хранить один логический объект в одном стабильном файле, а README использовать как индекс; уникальность ID и связи проверять validator.
- **Проверка:** два независимых добавления меняют разные object files; validator отклоняет duplicate ID и сломанные связи.

## Notes

Trial до появления второго независимого проекта или воспроизводимого concurrency test.
