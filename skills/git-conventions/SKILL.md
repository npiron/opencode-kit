---
name: git-conventions
description: Use for git workflows: committing, branching, creating PRs, code review, and GitHub operations. Trigger with keywords: commit, push, PR, pull request, merge, branch, review, code review, github, convention.
---

# Git & GitHub Conventions

## Commits

Format: `<type>(<scope>): <description>`

Types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`, `perf`, `ci`

Examples:
- `feat(scraper): add anti-detection headers`
- `fix(mcp): resolve playwright timeout on slow pages`
- `refactor(skills): split scraper into sub-skills`

Rules:
- Lowercase description, no trailing period
- Max 72 characters for the description
- Atomic commits: one logical change = one commit
- Never commit secrets, tokens, `.env`

## Branches

- `main`: production
- `feat/<name>`: new features
- `fix/<name>`: bug fixes
- `refactor/<name>`: refactoring

## Pull Requests

- Descriptive title
- Description: what, why, how to test
- Link the issue with `Closes #X`
- Request review before merge
- Squash merge for feature branches

## Code Review via GitHub MCP

- Use `@modelcontextprotocol/server-github` to list PRs, read diffs, post comments
- Check: style, performance, security, tests, docs
- Approve or request changes with constructive comments

## Do Not

- `git push --force` on `main`
- Commit directly to `main`
- Commit large files (>5MB) without Git LFS
- Amend commits already pushed to a shared branch
