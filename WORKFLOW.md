# GitHub Repository & Team Workflow

## Branching Strategy

### Main Branch
- **Main** branch holds only releasable, production-ready code
- Direct commits to main are prohibited
- All work flows through feature branches and pull requests

### Feature Branch Naming Convention
Branches follow the pattern: `[type]/[short-description]`

**Types:**
- `feature/` - new capabilities or analytics features
- `fix/` - bug fixes
- `docs/` - documentation only
- `refactor/` - code cleanup without behavior changes
- `chore/` - maintenance tasks, dependency updates

**Examples:**
- `feature/customer-churn-prediction`
- `fix/revenue-calculation-bug`
- `docs/data-dictionary-update`
- `refactor/extract-validation-logic`
- `chore/update-requirements`

### Branch Lifecycle
1. Create feature branch from main: `git checkout -b feature/description`
2. Work and commit on feature branch
3. Push to GitHub: `git push origin feature/description`
4. Open Pull Request to main
5. Code review and approval required
6. Merge to main
7. Delete feature branch after merge

---

## Commit Message Convention

### Format
```
[type]: [description]

[optional body explaining why this change matters]
```

### Types
| Type | Usage | Example |
|------|-------|---------|
| **feat** | New feature or capability | `feat: add revenue anomaly detection algorithm` |
| **fix** | Bug fix or correction | `fix: correct null percentage calculation in profiler` |
| **docs** | Documentation changes only | `docs: add data ingestion process to README` |
| **refactor** | Code cleanup, no behavior change | `refactor: extract CSV validation into utils module` |
| **test** | Add or modify tests | `test: add unit tests for revenue aggregation` |
| **chore** | Maintenance, dependencies | `chore: update pandas to 2.0 in requirements.txt` |

### Guidelines
- Keep message under 72 characters when possible
- Use imperative mood: "add" not "added", "fix" not "fixed"
- Explain the "why" in the body, not just the "what"
- Reference issue numbers in body: `Closes #123`

### Example Commits
```
feat: implement data quality scoring system

Adds automated quality checks for incoming datasets.
Validates schema completeness, missing values, and outliers.
Generates quality report before pipeline processes data.

Closes #5

---

fix: correct revenue aggregation logic

Fixed double-counting in monthly revenue calculation.
Was summing both transaction and adjustment records.
Now correctly uses only final transaction records.

---

docs: document data dictionary for analytics team

Adds complete column definitions and business rules
for customer, transaction, and revenue tables.
```

---

## Pull Request Process

### When to Create a PR
- Feature branch has at least 1-3 commits
- Code is tested and ready for review
- Related GitHub issue exists

### PR Description Template
```
## Summary
[1-2 sentence overview of what changed]

## What Changed
- [Bullet point: change 1]
- [Bullet point: change 2]
- [Bullet point: change 3]

## Related Issue
Closes #[issue-number]

## Testing
[How you tested this change]

## Checklist
- [ ] Commit messages follow convention
- [ ] Code is tested
- [ ] No sensitive data or credentials in code
```

### Merge Requirements
- **Minimum 1 approval** from a team member
- **All commits** reviewed and understood
- **Commit messages** checked for clarity
- **Tests pass** (when applicable)

### After Merge
- Feature branch is deleted
- Related issue is automatically closed
- Work moves to "Done"

---

## GitHub Issue Tracking

### Issue Lifecycle
1. **Create** issue in GitHub with clear title and description
2. **Assign** to responsible team member
3. **Label** with category (feature, bug, documentation, etc.)
4. **Link** to PR when work begins: `[PR link]`
5. **Close** automatically when PR is merged (via "Closes #123" in PR description)

### Issue Requirements
Every issue must have:
- **Title**: Action-oriented and specific
  - ✅ "Ingest customer transaction data into pipeline"
  - ❌ "data ingestion"
- **Description**: Context and success criteria
- **Label**: At least one category label
- **Assignee**: Single responsible person

### Label Categories
- `feature` - new capability
- `bug` - something broken
- `documentation` - docs only
- `data-pipeline` - pipeline work
- `analysis` - analytical task
- `high-priority` - urgent
- `in-progress` - currently being worked on

---

## Team Responsibilities

### As a Contributor
1. Create or pick an issue from the backlog
2. Assign issue to yourself
3. Create feature branch with proper naming
4. Make commits with clear messages
5. Push to GitHub
6. Open PR with issue link
7. Request review from teammate
8. Address feedback and update commits
9. Wait for approval before merge

### As a Reviewer
1. Review code for: correctness, clarity, data integrity
2. Check commit messages follow convention
3. Verify issue link in PR description
4. Request changes or approve
5. Leave comments explaining any concerns
6. Approve only when satisfied

---

## Quick Reference

### Creating Work
```
1. Create GitHub issue
2. git checkout -b feature/description
3. Make changes
4. git commit -m "type: description"
5. git push origin feature/description
6. Open PR with "Closes #[issue]" in description
```

### Reviewing Work
```
1. Read PR description and issue
2. Review commits and commit messages
3. Review code changes
4. Approve or request changes
5. Comment with feedback
```

### Merging Work
```
1. PR has 1+ approval
2. Commit messages reviewed
3. All feedback addressed
4. Click "Merge pull request"
5. Delete feature branch
```

---

## Why This Matters

✅ **Isolation**: Each person works independently without blocking others  
✅ **Safety**: Main branch never breaks - broken code stays in feature branches  
✅ **Traceability**: Every line of code has a linked issue explaining why it exists  
✅ **Quality**: Code review catches bugs before production  
✅ **History**: Clear commit messages let future you (or teammates) understand decisions  
✅ **Rollback**: Bad changes can be reverted with a single commit
