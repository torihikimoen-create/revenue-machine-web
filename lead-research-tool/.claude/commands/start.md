Read the following files in this exact order before doing anything else. Do not skip any of them.

1. `CLAUDE.md` — project rules and constraints
2. `SESSION_LOG.md` — full history of every previous session
3. `TASK_REGISTRY.md` — every task ever created, with current status
4. `DECISIONS.md` — architectural decisions that must not be contradicted
5. `COMMENTS.md` — verbatim user comments (sacred — never lose these)
6. `FEATURE_LIST.json` — pass/fail feature tracker
7. Read the last 3 files in `plans/` if that directory exists

After reading all files, do the following:

**Cross-reference check:**
- List every task in TASK_REGISTRY.md with status `in-progress` or `pending`
- Check the last 3 plans for items not yet in the task registry — flag as "dropped task" if found
- Check for any uncommitted or unpushed git changes: run `git status` and `git log origin/main..HEAD --oneline`

**Session recovery summary:**
Output a structured summary in this format:

```
SESSION RECOVERY — AETHERCORE lead-research-tool
=================================================
Last session: [date and session ID from SESSION_LOG.md]
Last session summary: [1-2 sentences from SESSION_LOG.md]

PENDING TASKS ([count]):
- [task ID] [description] — [status]

IN-PROGRESS TASKS ([count]):
- [task ID] [description]

DROPPED TASKS (in plan but not in registry) ([count]):
- [description]

GIT STATE:
- Uncommitted changes: [yes/no — list files if yes]
- Unpushed commits: [yes/no — list if yes]

READY TO WORK.
```

If this is the first run (SESSION_LOG.md is empty or contains only the template header), do the following instead:

1. Say: "First run detected. Setting up safeguard files for AETHERCORE lead-research-tool."
2. Initialize SESSION_LOG.md — replace `{PROJECT_NAME}` with `AETHERCORE lead-research-tool`
3. Initialize TASK_REGISTRY.md — replace `{PROJECT_NAME}` with `AETHERCORE lead-research-tool`
4. Initialize DECISIONS.md — replace `{PROJECT_NAME}` with `AETHERCORE lead-research-tool`
5. Initialize FEATURE_LIST.json — replace `{PROJECT_NAME}` with `AETHERCORE lead-research-tool`, `{DATE}` with today's date
6. Initialize COMMENTS.md — replace `{PROJECT_NAME}` with `AETHERCORE lead-research-tool`
7. Confirm: "Safeguard files initialized. Type any task to begin."
