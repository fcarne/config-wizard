# Tasks

## 1. The ruleset file and the documents

- [x] 1.1 Create `.github/rulesets/protect-main.json` as designed: name `protect-main`, target `branch`, enforcement `active`, `bypass_actors` empty, a condition including only `refs/heads/main`, and the rules `deletion`, `non_fast_forward`, `pull_request` (zero required approvals) and `required_status_checks` (context `ci`, `integration_id` 15368, strict false). Before writing it, check the field names against GitHub's REST reference for repository rulesets. Verify `python3 -m json.tool .github/rulesets/protect-main.json` succeeds and `uv run pre-commit run --all-files` passes.
- [x] 1.2 In `AGENTS.md`, add a short section on repository rules: what the ruleset enforces and that it has no bypass, that merges are squash-only with the commit subjects in the body and merged branches deleted, that `.github/rulesets/protect-main.json` is the source to reapply, and how to roll back. Verify `grep -n "protect-main" AGENTS.md` shows the section and the text matches the design's settings.
- [x] 1.3 In `ROADMAP.md`, delete the `protect-main-branch` item and renumber the rest. Verify the numbering is consecutive from 1 and `test-streamlit-backend` is first.
- [x] 1.4 Run `openspec validate protect-main-branch --strict`. Verify it reports the change as valid.

## 2. Open the pull request

- [x] 2.1 Commit the group-1 work with one single-line gitmoji subject, push the branch, open the pull request and wait for CI. Verify `gh pr checks` shows `checks`, all eight `tests` cells and `ci` passing, while `main` is still unprotected.

## 3. Apply the settings

Ask the user for confirmation before each step in this group; the commands change the live repository.

- [x] 3.1 Record the state to restore: save the output of `gh api repos/fcarne/config-wizard` fields `allow_merge_commit`, `allow_rebase_merge`, `delete_branch_on_merge`, `squash_merge_commit_title` and `squash_merge_commit_message`, and the empty rulesets list, in the pull request description. Verify the recorded values equal the Migration Plan's list.
- [x] 3.2 Create the ruleset with `gh api --method POST repos/fcarne/config-wizard/rulesets --input .github/rulesets/protect-main.json`. Verify the call returns an id, `gh api repos/fcarne/config-wizard/rulesets/<id>` returns enforcement `active` with empty `bypass_actors`, and its rules equal the file's.
- [x] 3.3 Set `allow_merge_commit` false, `allow_rebase_merge` false and `delete_branch_on_merge` true with `gh api --method PATCH repos/fcarne/config-wizard`. Verify the read-back shows those three values and the squash title and message settings are unchanged.

## 4. Verify enforcement

- [x] 4.1 Run `gh api repos/fcarne/config-wizard/rules/branches/main`. Verify it lists `deletion`, `non_fast_forward`, `pull_request` and `required_status_checks`, and that the `ci` check run's app id on the pull request's head commit is 15368.
- [x] 4.2 With the user's confirmation, in a scratch clone push one empty commit straight to `main`. Verify the push is rejected with a ruleset violation and `git ls-remote origin main` still shows the commit it showed before the push. If the push lands, report it, revert nothing (an empty commit changes no file) and treat the ruleset as not enforcing.
- [x] 4.3 Verify `gh pr view <number> --json mergeStateStatus` reports `CLEAN` for the green pull request, then merge it with `gh pr merge --squash`. Verify the merge succeeds, `git log -1 origin/main` shows one commit whose body lists commit subjects, the head branch is gone (`gh api repos/fcarne/config-wizard/branches --jq '.[].name'` prints only `main`), and `gh pr merge --merge` on a scratch pull request is refused.

## Workflow follow-up

- Archive the change after the merge; the archive pull request is the first to go through the new rules.
- The first Dependabot pull request after this change should show `ci` running and passing; if it does not, adjust the ruleset.
- Continue with `test-streamlit-backend`.
