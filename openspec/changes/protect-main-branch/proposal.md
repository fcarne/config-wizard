# Proposal

## Why

The `ci` check exists and passes, but nothing makes it count: `main` has no ruleset and no protection, so anyone with write access, including the maintainer, can push to it directly, force-push it, delete it, or merge a pull request whose checks failed. The repository also still allows merge commits and rebase merges, which let multi-line commits reach `main` in other ways than the squash message. The roadmap placed this change after the first green CI run, which has now happened (PR #17 and PR #20).

## What Changes

- Add a repository ruleset `protect-main` on `main`, enforced for everyone with no bypass actors (the maintainer included): changes must arrive through a pull request with zero required approvals, the `ci` check must pass (pinned to the GitHub Actions app), and deletion and force-pushes are blocked. The branch does not have to be up to date before merging.
- Change the repository merge settings: allow squash merges only (merge commits and rebase merges off) and delete the head branch after a merge. The squash message stays `COMMIT_MESSAGES`: the body lists the subjects of the pull request's commits, which are single-line because the `commit-msg` hook enforces it.
- Commit the ruleset as `.github/rulesets/protect-main.json`, in the shape the create-ruleset API accepts, so it can be reviewed in a pull request and reapplied.
- Record the rules in `AGENTS.md`, correct the roadmap item (the `BLANK` squash message is dropped), and remove the item once the change is archived.
- No library behavior changes. This is repository configuration and documentation, so the change sets `skip_specs: true`.

## Capabilities

### New Capabilities

None. This change is repository configuration only.

### Modified Capabilities

None. No requirement in `openspec/specs/` describes repository settings.

## Impact

- New file: `.github/rulesets/protect-main.json`.
- Changed files: `AGENTS.md`, `ROADMAP.md`.
- Repository settings changed through the GitHub API, outside the git history: one new ruleset, `allow_merge_commit`, `allow_rebase_merge` and `delete_branch_on_merge`.
- Out of scope, each already its own roadmap item: `lint-pull-request-titles`, `add-coverage-gate`, and requiring that a branch is up to date before merging, which can be added later as one ruleset field.
