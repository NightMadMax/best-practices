---
type: reference
status: active
owner: project
last_verified: 2026-07-06
source_of_truth: scripts/search_practices.py
related:
  - "[[docs/reference/PRACTICE_SCHEMA]]"
  - "[[practices/README]]"
---

# Поиск по каталогу практик

Полный Markdown-каталог:

```sh
make catalog
```

Фильтры можно повторять; несколько tags имеют AND-семантику:

```sh
python3 scripts/search_practices.py \
  --section common \
  --status accepted \
  --tag security \
  --query credentials \
  --format json
```

Каталог включает все lifecycle statuses и всегда показывает status/evidence.
Consumer delivery по-прежнему исключает `deprecated` и `superseded`; search не
является командой применения.
