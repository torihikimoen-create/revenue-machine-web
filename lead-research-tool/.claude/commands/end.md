Perform a clean session wrap-up. Execute every step in order.

**Step 1 — Review this session**
- List all tasks completed this session (status changed to `done`)
- List all tasks still `pending` or `in-progress`
- List any decisions made this session

**Step 2 — Update safeguard files**

Update `SESSION_LOG.md` — append a new entry:
```
---
## Session [next session number] — [today's date]
**Summary:** [2-3 sentence summary of what was done]
**Tasks completed:** [list]
**Tasks remaining:** [list with IDs]
**Decisions made:** [list or "none"]
**Next session should start with:** [top priority]
```

Update `TASK_REGISTRY.md` — ensure every task from this session has correct final status (`done`, `pending`, `blocked`)

Update `COMMENTS.md` — log any user comments from this session that haven't been logged yet

Update `DECISIONS.md` — add any new architectural decisions made this session

Update `FEATURE_LIST.json` — update pass/fail status for any features touched this session

**Step 3 — Archive plans**
If any plans were created this session and not yet archived, copy them to `plans/S{session}-{seq}_{description}.md`

**Step 4 — Commit and push**
Run:
```
git add -A
git status
```
Show the list of changed files and ask: "Commit all the above? (y/n)"

If confirmed:
```
git commit -m "S{session}-{seq}_session-end: [brief summary]"
git tag "S{session}-{seq}_session-end" HEAD
git push && git push --tags
```

**Step 5 — Verify clean state**
Run `git status` — confirm clean working tree.

**Step 6 — Output final summary**
```
SESSION END SUMMARY
===================
Session: [ID]
Completed: [count] tasks
Pending: [count] tasks
Committed: [yes/no]
Pushed: [yes/no]

Top priority for next session:
- [single most important next task]

Type /start next session to recover full context.
```
