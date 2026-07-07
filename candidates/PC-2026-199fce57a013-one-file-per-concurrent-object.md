---
id: PC-2026-199fce57a013
status: triaged
source: "Best Practices: docs/quality/DEFECTS.md, общий staging кандидатов"
added_by: "Codex по подтверждённому дефекту BP"
stack: common
target: practices/common/PC-2026-199fce57a013-one-file-per-concurrent-object.md
evidence_level: E1
evidence: "BP defect: общая таблица кандидатов вызывала merge conflicts; исправлено переходом на file-per-object"
created: 2026-07-07
decided:
---

# Храните независимо изменяемые объекты в отдельных файлах

- **Контекст:** несколько участников создают и принимают однотипные записи через независимые pull request.
- **Проблема:** единая таблица или общий агрегат превращает несвязанные изменения в конфликтующие правки одного файла.
- **Решение:** хранить один логический объект в одном стабильном файле, а общий README использовать только как навигацию; проверять уникальность ID и связи автоматическим validator.

## Notes

На harvest-этапе evidence ограничен BP. Воспроизводимые repository tests будут отдельно оценены review-этапом.
