---
type: how-to
status: active
owner: project
last_verified: 2026-07-07
source_of_truth: scripts/migrate_consumer_manifest.py
related:
  - "[[docs/reference/PRACTICE_SCHEMA]]"
  - "[[docs/architecture/decisions/ADR-0006-versioned-consumer-manifest]]"
  - "[[docs/quality/DEFECTS]]"
---

# Миграция consumer manifest

По умолчанию команда строит read-only plan:

```sh
python3 scripts/migrate_consumer_manifest.py --project "/path/to/project"
```

Plan требует отдельный чистый Git repository, отклоняет symlink и выводит
preimage SHA-256 с fingerprint. Canonical schema 1 сохраняет все practice
outcomes; legacy `optout=true` становится `preferences.global=optout`.
Неизвестное секционное `applied` получает `manual_review_required`.

После review применить тот же plan:

```sh
python3 scripts/migrate_consumer_manifest.py \
  --project "/path/to/project" \
  --apply \
  --fingerprint "<64-hex>" \
  --yes
```

Apply повторно проверяет clean tree и preimage, пишет через temporary file и
atomic replace, затем проверяет schema 2. Изменение остаётся unstaged; его нужно
проверить и закоммитить в consumer repository. После commit повторный plan
возвращает `up_to_date`.
