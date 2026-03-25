Run a full integrity audit. Check everything — do not skip steps.

**1. Task registry integrity**
- Read TASK_REGISTRY.md in full
- List all tasks with status `in-progress` — flag any that have been in-progress for more than 1 session
- List all tasks with status `blocked` — confirm each has a reason recorded
- Check for duplicate task IDs

**2. Plan cross-reference**
- Read all files in `plans/` directory
- For every item in every plan, verify it exists in TASK_REGISTRY.md
- Flag as "DROPPED TASK" any plan item not in the registry

**3. Decision consistency**
- Read DECISIONS.md
- Check if any recent code changes contradict recorded decisions
- Run `git log --oneline -20` and cross-reference commits against the task registry — flag any commit not traceable to a task

**4. Git state**
- Run `git status` — flag any uncommitted changes
- Run `git log origin/main..HEAD --oneline` — flag any unpushed commits
- Run `git stash list` — flag any stashed changes

**5. File integrity**
- Confirm all 6 safeguard files exist: SESSION_LOG.md, TASK_REGISTRY.md, DECISIONS.md, COMMENTS.md, FEATURE_LIST.json, CLAUDE.md
- Confirm FEATURE_LIST.json is valid JSON
- Flag any safeguard file that appears to be at template state (still contains `{PROJECT_NAME}`)

**6. Unarchived plans**
- Check if any plans exist in `~/.claude/plans/` that have not been copied to `plans/`

**Output format:**
```
AUDIT REPORT — [timestamp]
==========================

PASSING: [count]
WARNINGS: [count]
CRITICAL: [count]

--- PASSING ---
[list]

--- WARNINGS ---
[list — non-blocking issues]

--- CRITICAL ---
[list — must be fixed before continuing work]

RECOMMENDATION: [one sentence on what to do next]
```
