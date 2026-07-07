---
type: code-review
status: complete
owner: project
last_verified: 2026-07-07
source_of_truth: .best-practices.json
related:
  - "[[docs/how-to/MIGRATE_CONSUMER_MANIFEST]]"
  - "[[docs/quality/DEFECTS]]"
---

# Review A5: BP consumer manifest migration

## Reviewed plan

- preimage SHA-256: `78792396035a6af9abe5466576593826865460a3de4d675948083d57bb41c5d5`;
- fingerprint: `0791b4a84c2ec753a9e0662e13f882cf742670e44bd8e37d0a9297bdbcc8e469`;
- transition: schema 1 → 2.

## Diff review

Добавлены только canonical `preferences` (`global=ask`, пустые sections) и
`schema_version=2`. Три practice outcomes, включая `not-applicable`, сохранены
без изменения каждого поля.

## Verification

- apply проверил clean Git tree, reviewed fingerprint и preimage;
- canonical loader принимает schema 2;
- migration unit suite и полный `make check` проходят;
- NPR writer defect закрыт опубликованными NPR PR №15/16 и real-code E2E.

## Verdict

Миграция BP принята; recorded consumer evidence сохранена.
