Apply the Itemisation Protocol to code files in this project.

**Step 1 — Check if enabled**
Read CLAUDE.md and check for `ITEMISATION: disabled`. If found, stop immediately and say: "Itemisation is disabled for this project (ITEMISATION: disabled in CLAUDE.md). To enable, change it to ITEMISATION: enabled."

**Step 2 — Select files**
List all code files in the project (`.py`, `.ts`, `.tsx`, `.js`, `.sql`). Exclude:
- `node_modules/`, `__pycache__/`, `.git/`, `venv/`
- Files under 30 lines
- Test files (names starting with `test_`)

Show the list and ask: "Apply itemisation to these [N] files? (y/n)"

**Step 3 — Backup**
For each confirmed file, create `{filename}.itemise-backup` as an exact copy before touching anything.

**Step 4 — Apply numbering**
Add hierarchical section numbers to each file following these rules:

Number these blocks:
- Top-level sections: `# 1. SECTION: Name` ... `# end of 1`
- Functions/methods: `# 1.1 function_name()`  ... `# end of 1.1`
- Significant conditionals with business logic: `# 1.1.1 Description`
- Important loops with non-trivial bodies: `# 1.1.2 Description`
- Key config objects: `# 1.2.1 Description`

Do NOT number:
- Variable declarations
- Single-line assignments
- Imports
- Closing braces / trivial boilerplate

Comment syntax by language:
- Python, YAML, Shell: `# 1.1 Description`
- JS, TS: `// 1.1 Description`
- HTML: `<!-- 1.1 Description -->`
- CSS: `/* 1.1 Description */`
- SQL: `-- 1.1 Description`

Target depth: 3 levels (`1.2.3`) for most code, 4 only for genuinely complex nested config.

**Step 5 — Verify integrity**
For each modified file:
1. Strip all added comment-number lines
2. Diff the stripped version against the `.itemise-backup`
3. If any diff exists beyond whitespace, restore from backup immediately and report: "INTEGRITY FAILURE: {filename} — restored from backup. No code was changed."

**Step 6 — Clean up**
Delete all `.itemise-backup` files on success.

**Step 7 — Report**
```
ITEMISATION COMPLETE
====================
Files processed: [count]
Files skipped: [count and reasons]
Integrity failures: [count — should be 0]

Files itemised:
- [filename] — [N sections added]
```
