# Fork-Specific Notes (`kargnas/codex-lb`)

This file tracks fork-specific patches, upstream sync history, and fork maintenance rules.
It is additive to [AGENTS.md](./AGENTS.md) and should stay short, factual, and easy to update.

## Purpose

- Keep this fork easy to re-sync from upstream.
- Record fork-only behavior that must survive upstream merges.
- Make upstream conflict resolution decisions explicit.

## Remotes

- `origin`: `https://github.com/kargnas/codex-lb.git`
- `upstream`: `https://github.com/Soju06/codex-lb.git`

Do not remove `upstream`. Upstream sync work should continue to use the `upstream-fork-sync` skill.

## Branch Strategy

- Long-lived fork branch: `kars`
- Upstream default branch: `main`
- Do fork maintenance and customizations on `kars` unless there is a clear reason to use a short-lived branch.

## Conflict Resolution Policy

- Default to upstream behavior unless a fork-specific requirement is intentional and documented here.
- Preserve fork-only behavior only when its purpose, affected files, and verification notes are recorded.
- Prefer minimum-diff changes for fork-only fixes so the next upstream merge stays cheap.

## Upstream Sync History

| Date | Upstream Tag | Commit | Notes |
|------|--------------|--------|-------|
| 2026-03-31 | `v1.8.3` | `90d0983` | Merged upstream v1.8.3; resolved load_balancer.py conflicts (adopted upstream select_account simplification); no active fork patches |
| 2026-03-23 | `v1.8.0` | `0cad3f3` | Merged upstream `v1.8.0` into `kars` and revalidated targeted tests |

## Active Fork Patches

No fork-only patches are formally tracked yet.

When adding one, use this format:

### `<type(scope): short title>`

- Reason:
- Files:
- Upstream status:
- Verification:

## Merge Checklist

- Check whether the patch still exists after upstream sync.
- Check whether the patch's call sites still exist after upstream sync.
- Remove the patch if upstream now provides the same behavior.
- Update this file in the same commit whenever a fork-only patch is added, removed, or changed.
