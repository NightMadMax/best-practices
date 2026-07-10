# Agent Instructions

## Communication Language

- Always answer the user in Russian, including research, reviews, plans,
  progress updates, and final reports.
- Preserve commands, paths, identifiers, API names, and original error messages
  when translating them would reduce technical accuracy.
- Use another language only when the user explicitly requests it.

## Project Identity

- Project: `Best Practices`
- This folder is the git repository root and a project folder inside the parent
  Obsidian vault.
- Project navigation: [[README]], [[INDEX]], and [[PROJECT]].

## Commands

- `make check` — полный локальный gate: tests, schema/link validation и strict
  freshness checks. Запускай перед завершением любой repository change.
- `make test` — только unit и workflow tests через `unittest`.
- `make validate` — schema, lifecycle, secrets и Markdown/wikilink validation.
- `make freshness` — strict-проверка просроченных практик.
- `make metrics` — сводные maturity/freshness metrics.
- `make catalog` — локальный поиск по каталогу практик.

## Done when

- `make check` проходит полностью.
- Изменение проверено по `git diff`; в commit не попали secrets, generated
  noise или несвязанные пользовательские изменения.
- Новые или перемещённые Markdown-артефакты связаны wikilinks, а `INDEX.md` и
  `docs/README.md` обновлены, если изменилась навигация.
- Обнаруженные дефекты записаны в `docs/quality/DEFECTS.md`; исправленные
  перенесены в `Fixed` с датой, commit и root cause.
- Изменение закоммичено и отправлено в текущую remote branch. PR, release и
  иные remote actions выполнены только после отдельного согласования.

## Markdown Workflow

- Edit Markdown files directly in the project folder.
- Do not use an Obsidian REST API, helper script, synchronization step, or
  duplicate Markdown copy.
- `AGENTS.md` is the single source of agent rules. `CLAUDE.md` only contains
  `@AGENTS.md` so Claude Code reads the same file; keep all rules in `AGENTS.md`.
- If a subdirectory needs scoped instructions, create an adjacent
  `AGENTS.md`/`CLAUDE.md` pair. Scoped rules must specialize broader rules
  without contradicting them. An `AGENTS.override.md` replaces a level entirely;
  plain `AGENTS.md` is concatenated with parent levels.
- Keep `AGENTS.md` compact: Codex truncates the instruction chain past
  `project_doc_max_bytes` (32 KiB by default). Move topic detail into `docs/`.
- Do not edit `AGENTS.md` or `CLAUDE.md` mid-session; it invalidates the cached
  prompt prefix. Record new rules between sessions.
- Keep `INDEX.md` current when files change purpose or location.
- Use wikilinks for relationships between Markdown notes; code-formatted paths
  do not create Obsidian graph connections.

## Rule Authoring

- Keep instruction files compact. Codex stops adding files when the combined
  instruction chain reaches `project_doc_max_bytes` (32 KiB by default); move
  detailed workflows into docs or skills.
- Prefer specific negative instructions ("don't use X — use Y") and exact
  commands over prose like "write clean code".
- Lead with the most critical, non-negotiable rules and group them by task.
- State the reason, then the rule; avoid vague directives and aspirational rules
  not reflected in the codebase.
- Verify changed rules in a new non-interactive process and check the loaded
  instruction sources and precedence.

## Repository Workflow

- Use a separate GitHub repository for this project.
- Commit and push completed repository changes unless the user asks not to.
- Ask before pull requests, releases, issues, remote changes, or destructive
  history operations.
- Keep paths relative and account for macOS and Windows differences.
- Never run two agents at the same time in this working copy; parallel agents
  belong in separate git worktrees.

## Tool Selection

- Use the project's existing language and toolchain first.
- Prefer standard tools already available on all target machines; ask before
  adding third-party dependencies.
- Prefer Python 3 standard-library code for non-trivial reusable
  cross-platform automation when Python is available everywhere it must run.
- Prefer `git`, `rg`, POSIX shell, or PowerShell for simple native operations.
- Keep shell and PowerShell wrappers when Python cannot be assumed on a clean
  target machine.
- If a missing tool is materially better than available substitutes, explain
  what is needed and why, then ask the user for permission before installing
  it instead of silently using a lower-quality workaround.
- After approval, install through the normal package manager, verify the
  version, and document project-specific tooling in `TOOLS.md` or its manifest.

## Documentation

- Required core: `README.md`, `AGENTS.md`, `INDEX.md`, and `PROJECT.md`.
- Keep durable artifacts under `docs/`.
- When `docs/` exists, keep `docs/README.md` as its connected index.
- Store one decision per ADR, one investigation per research file, and one code
  review per review file.
- Use `ACTIONS.md` only for consequential actions outside git.
- Do not create empty documents without a current purpose.
- Treat API specifications, lock files, generated SBOM files, and
  `.github/CODEOWNERS` as authoritative.
- Never commit secrets or real credentials.

## Knowledge Promotion

- Keep project-specific facts, architecture, defects, decisions, research, and
  operational knowledge in this project.
- Treat Codex and Claude generated memory as local working state. Never commit
  raw memory directories.
- Promote a lesson into the shared `new-project-rules` standard only when it is
  reusable across projects, independent of private context, and can become a
  rule, template, test, validator, script, or skill.
- Record the source artifact, evidence, intended scope, and verification date;
  remove secrets, personal data, private identifiers, and machine-specific paths.
- Preserve the original record and promote an abstracted conclusion, not raw
  incident, defect, conversation, or memory text.
- When applicability is uncertain, keep the knowledge here and ask the user
  before changing the shared standard.

## Defect Tracking

- Record every discovered defect, bug, or known issue in
  `docs/quality/DEFECTS.md` immediately upon discovery.
- Include a short title, discovery date, and description. Status is represented
  by the section where the entry lives: `Open`, `Fixed`, or `Won't Fix`.
- When fixed, move the entry to `Fixed` and add the fix date, commit reference,
  and root cause when known.
- Check existing open defects before changing the affected component.
- If the defect log does not exist, create it from the shared project template.

## Pattern Playbook

- Record a verified, reusable successful pattern in `docs/quality/PLAYBOOK.md`
  once it has proven correct at least twice — the success-side counterpart to
  the defect log, so the agent repeats the known-good approach.
- Each entry includes a short title, the date added, the component, the concrete
  known-good steps, and the evidence (commits/PRs or a passing test).
- Keep entries project-specific; propose cross-project patterns for promotion.
  Create the file from the template the first time a pattern qualifies; do not
  pre-create it empty.

## Reflexive Learning

- After a mistake or a user correction, before moving on, reflect on the root
  cause, abstract it beyond the specific case, and record the lesson where it
  belongs: `DEFECTS.md` for a bug, `PLAYBOOK.md` for a verified good approach,
  `AGENTS.md` for a project rule (between sessions), or a promotion proposal when
  the lesson is reusable across projects.
- Record only abstractable, recurring lessons; skip one-off typos and noise.
