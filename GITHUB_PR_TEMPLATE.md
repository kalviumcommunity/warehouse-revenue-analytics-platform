# Pull Request Template - Copy & Paste Into GitHub PR

---

## PR Title
```
Add data ingestion workflow and team branching guidelines
```

## PR Description

```
## Summary
Establishes the data ingestion workflow, documents team collaboration standards, and implements branching strategy for preventing code conflicts and maintaining code quality.

## What Changed
- **WORKFLOW.md**: Complete documentation of branching strategy, commit conventions, and PR review process for team
- **feat: data ingestion function** - Validates incoming CSV files for schema completeness before processing
- **docs: updated requirements.txt** - Added validation dependencies (pandas, pydantic for schema validation)
- **feat: data quality report generator** - Creates quality metrics for incoming datasets
- **docs: data dictionary** - Documented column definitions and business rules for team reference

## Key Implementation Details

### Branching Strategy
- Main branch holds only production-ready code
- Feature branches follow `feature/[description]` naming convention
- All code goes through PR review before merge
- Branches deleted after successful merge

### Commit Message Convention
Format: `[type]: [description]`

Types used:
- `feat` - New features (data validation, quality reporting)
- `docs` - Documentation (WORKFLOW.md, data dictionary, README updates)
- `chore` - Dependencies and maintenance (requirements.txt updates)

### Code Review Process
- Minimum 1 approval required before merge
- Reviewer checks: correctness, clarity, data integrity, test coverage
- Commit messages reviewed as part of code review
- All feedback must be addressed before merge

## Related Issues
Closes #1 - Ingest customer transaction data into pipeline
Closes #2 - Create data quality report for incoming datasets
Closes #3 - Document data dictionary for team reference

## Testing
- ✅ Data validation function tested with sample CSV files (valid and invalid schemas)
- ✅ Quality report generator tested on sample datasets
- ✅ Data dictionary validated against actual column structures
- ✅ No errors on valid files; appropriate errors raised on invalid schema
- ✅ All imports and dependencies verified

## Checklist
- [x] Feature branch created with proper naming convention
- [x] At least 3 commits with conventional message format
- [x] All commits have descriptive messages explaining "why" not just "what"
- [x] Commit messages follow `[type]: [description]` format
- [x] Code tested and working
- [x] No sensitive data or credentials in code
- [x] WORKFLOW.md documents branching and commit strategy
- [x] Related GitHub issues linked with "Closes #X"
- [x] Ready for team review

## How to Review
1. Read this PR description to understand context
2. Review linked issues (#1, #2, #3) for requirements
3. Examine each commit and commit message quality
4. Review code changes for correctness and clarity
5. Verify no sensitive data is included
6. Approve when satisfied

## Merge Instructions
1. Verify 1+ approval is granted
2. Ensure all feedback is addressed
3. Click "Squash and merge" or "Create a merge commit"
4. Delete feature branch after merge
5. Issues will auto-close due to "Closes #X" links
```

---

## How to Create This PR on GitHub

1. Go to your repository → **Pull Requests** tab
2. Click **New Pull Request**
3. Select base: **main**, compare: **feature/github-workflow-setup**
4. Click **Create Pull Request**
5. Copy the PR Title into the title field
6. Copy the PR Description (everything between the triple backticks above)
7. Click **Create Pull Request** (do NOT merge yet - leave it open)
8. Add a comment with link to this PR for your submission

**Result:** You'll have an open PR showing your feature branch, commits, and clear documentation of your team workflow
