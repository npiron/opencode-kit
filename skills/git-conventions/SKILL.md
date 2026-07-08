---
name: git-conventions
description: Use for git workflows: committing, branching, creating PRs, code review, and GitHub operations. Trigger with keywords: commit, push, PR, pull request, merge, branch, review, code review, github, convention.
---

# Git & GitHub Conventions

## Commits

Format : `<type>(<scope>): <description>`

Types : `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`, `perf`, `ci`

Exemples :
- `feat(scraper): add anti-detection headers`
- `fix(mcp): resolve playwright timeout on slow pages`
- `refactor(skills): split scraper into sub-skills`

Règles :
- Description en minuscules, sans point final
- Max 72 caractères pour la description
- Commits atomiques : un changement logique = un commit
- Ne jamais commiter de secrets, tokens, `.env`

## Branches

- `main` : production
- `feat/<nom>` : nouvelles fonctionnalités
- `fix/<nom>` : correctifs
- `refactor/<nom>` : refactoring

## Pull Requests

- Titre descriptif
- Description : quoi, pourquoi, comment tester
- Lier l'issue avec `Closes #X`
- Demander review avant merge
- Squash merge pour les branches de feature

## Code Review via GitHub MCP

- Utiliser `@modelcontextprotocol/server-github` pour lister PRs, lire diffs, poster des commentaires
- Vérifier : style, perfs, sécu, tests, docs
- Approuver ou demander des changements avec commentaires constructifs

## Ne pas faire

- `git push --force` sur `main`
- Commiter directement sur `main`
- Commiter des fichiers volumineux (>5MB) sans Git LFS
- Amender des commits déjà poussés sur une branche partagée
