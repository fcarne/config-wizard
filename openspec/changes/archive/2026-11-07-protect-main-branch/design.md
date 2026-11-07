# Design

## Context

See `proposal.md` for motivation. Evidence from read-only GitHub queries on `main` at `a87827c`; nothing was changed.

| # | Finding | Evidence |
|---|---------|----------|
| 1 | `main` is unprotected | `GET branches/main/protection` returns 404 "Branch not protected"; `GET rulesets` returns an empty list; the only branch is `main`; the repository is public and the viewer has ADMIN |
| 2 | The check to require exists | `main`'s last commit has check runs `checks`, `ci` and eight `tests (<python>, <resolution>)`; `ci` is reported by the `github-actions` app, id 15368 |
| 3 | `ci` is safe to require | The `ci` job runs with `if: always()` and fails unless `checks` and `tests` succeeded, so a failed or cancelled job cannot show as green through a skipped aggregator |
| 4 | Merge settings allow every method | `allow_squash_merge`, `allow_merge_commit` and `allow_rebase_merge` are all true; `delete_branch_on_merge` is false; squash title is `COMMIT_OR_PR_TITLE` and squash body is `COMMIT_MESSAGES`; `allow_auto_merge` and `allow_update_branch` are false |
| 5 | Squash bodies list commit subjects | The `COMMIT_MESSAGES` body is the list of the pull request's commit messages, and the `commit-msg` hook keeps each of those a single subject line (earlier squashes carried 10 to 19 line bodies, finding 8 of the archived `add-ci-pipeline` design) |

Constraints that shape the approach:
- The settings live on GitHub, not in git, so the change must say how to see them, how to reapply them and how to undo them.
- With no bypass actors, a bad ruleset blocks the maintainer's own pull requests too. The repository's Settings page stays available to an admin, so the ruleset can always be edited or deleted there without merging anything.
- GitHub's documentation was only partly confirmed while planning: the field list for a ruleset was found in third-party summaries and the REST reference, not checked against the live API (see Risks).

## Goals / Non-Goals

**Goals:**
- The `ci` status gates every change to `main`, with no exceptions.
- History on `main` can only be linear squash commits, and the branches of merged pull requests disappear.
- The rules can be read in the repository and reapplied from it.

**Non-Goals:**
- Required approvals (a sole maintainer cannot approve their own pull request), the up-to-date requirement, signed commits, linear-history or merge-queue rules, and pull request title linting.
- Changing the squash message or title settings.

## Decisions

### A ruleset, not classic branch protection
One ruleset named `protect-main` targets the branch `refs/heads/main`, `enforcement: active`, `bypass_actors: []`. Its rules are `deletion`, `non_fast_forward`, `pull_request` (zero required approvals, no thread or code-owner requirements) and `required_status_checks` with the single context `ci` and `integration_id` 15368, with `strict_required_status_checks_policy: false`.

Why a ruleset: it is exportable as JSON and can be committed, its bypass list is explicit (empty here), and the check can be pinned to the Actions app so that another app cannot satisfy `ci` by name. Classic protection has no export and a less explicit bypass story.

Alternative: classic branch protection with "include administrators". Rejected for the reasons above; it would have been simpler to apply.

### Bound by the rules
No bypass actors, including the repository admin. Alternative: allow the admin to bypass "for pull requests only", which leaves a way around the `ci` gate. Rejected: the point is that the gate has no exceptions.

### Zero approvals
The `pull_request` rule requires a pull request but no review, since the only maintainer cannot approve their own pull request and a required approval would deadlock the repository.

### Up-to-date branches are not required
`strict_required_status_checks_policy` stays false. Requiring it would force a rebase and a full ten-job rerun whenever another pull request merges. With one maintainer and squash-only history, two green pull requests that conflict semantically are rare; the flag can be turned on later with one edit.

### Squash only, delete merged branches, message settings unchanged
`allow_merge_commit` and `allow_rebase_merge` go to false so that squash is the only way in, and `delete_branch_on_merge` goes to true. The squash title and body settings are left as they are (`COMMIT_OR_PR_TITLE`, `COMMIT_MESSAGES`): the body lists the commit subjects, which the hook keeps single-line, so it holds no free text.

Alternative: set the body to `BLANK`, which was the original roadmap item. Rejected by the maintainer, who accepts the subject list.

### Commit the ruleset as JSON
`.github/rulesets/protect-main.json` holds the payload for `POST /repos/{owner}/{repo}/rulesets`. GitHub does not read this file, so it documents the intent and is the source for reapplying (`gh api --method POST ... --input`); a drift between it and the live ruleset is checked by reading the ruleset back.

Alternative: describe the rules only in `AGENTS.md`. Rejected: prose cannot be reapplied or diffed.

## Risks / Trade-offs

- [The API payload may not match what was assumed (empty `bypass_actors` meaning no bypass, `integration_id`, the `pull_request` parameters)] → Apply it, then read the ruleset back and compare it with the file, check that `GET rules/branches/main` lists the four rules, and check that the `ci` check run's app id is 15368. A mismatch is fixed before the change is archived.
- [The ruleset blocks the maintainer's own fixes] → The Settings page can edit or delete the ruleset without a pull request; this is the rollback path.
- [A failed enforcement test could land a commit on `main`] → The push test uses an empty commit, which is harmless if it lands, and it runs only after the user confirms.
- [A Dependabot pull request cannot merge if `ci` does not run for it] → Dependabot pull requests run the same workflow with the read-only token, and `ci` needs no secrets; the first Dependabot pull request after the change confirms it.
- [`COMMIT_MESSAGES` still bypasses the spirit of the one-line rule for commits that Dependabot authors] → Accepted; those commits are not covered by the `commit-msg` hook, and the squash body for them is longer than one line.

## Migration Plan

Before applying, the state to restore is: no ruleset; `allow_merge_commit` true, `allow_rebase_merge` true, `delete_branch_on_merge` false; squash title `COMMIT_OR_PR_TITLE` and body `COMMIT_MESSAGES` (unchanged by this change).

1. Merge nothing yet: open the pull request with the JSON file, `AGENTS.md` and `ROADMAP.md` changes and wait for a green `ci`.
2. After the user confirms, create the ruleset with `gh api` and change the three merge settings.
3. Verify as in `tasks.md`, then merge the pull request through the new rules, which proves a normal pull request still gets through.

Rollback: delete the ruleset from Settings or with `gh api --method DELETE repos/fcarne/config-wizard/rulesets/<id>`, and set the three merge settings back to the values above.
