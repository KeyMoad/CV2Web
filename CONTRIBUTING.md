# Contributing to CV2Web

Thanks for contributing! This document describes the branching model, development workflow, and basic rules for Pull Requests.

---

## Branches

### Protected branches
- **`main`**: Production / release branch (deploys from here)
- **`develop`**: Integration branch for the next release

Direct pushes to `main` and `develop` should be blocked. All changes must go through Pull Requests (PRs).

---

## Branch naming

Create a branch from `develop` using one of these prefixes:

- `feature/*` — new user-facing functionality
- `refactor/*` — restructuring code without changing behavior (ideally)
- `fix/*` — bug fixes (non-urgent)
- `chore/*` — maintenance tasks (deps, CI, formatting, docs, tooling)
- `hotfix/*` — urgent production fixes (branch from `main` only)

Examples:
- `feature/add-cli-export`
- `refactor/core-generator`
- `fix/null-handling-parser`
- `chore/update-dependencies`
- `hotfix/security-patch`

---

## Workflow

### 1) Create a work branch
All work starts from `develop` (except hotfixes):

1. Sync your local `develop`:
   - `git checkout develop`
   - `git pull origin develop`

2. Create your branch:
   - `git checkout -b <type>/<short-name>`

Example:
- `git checkout -b refactor/core-generator`

---

### 2) Commit rules
- Keep commits focused and small when possible
- Use clear messages (imperative mood)

Suggested commit message format:
- `type(scope): short summary`

Examples:
- `refactor(generator): simplify pipeline steps`
- `fix(parser): handle empty input`
- `chore(ci): run tests on pull requests`

---

### 3) Open a Pull Request to `develop`
1. Push your branch:
   - `git push -u origin <type>/<short-name>`

2. Open a PR:
   - Base: `develop`
   - Compare: your branch

3. PR requirements:
- At least 1 approval (recommended)
- No direct pushes to `develop`

After merge, delete the branch in GitHub.

---

## Releases

### Simple release (recommended)
When `develop` is ready:
- Open a PR from `develop` → `main`
- Merge it
- Optionally tag the release (e.g., `v1.2.0`)

---

## Hotfixes (urgent production fixes)

1. Create a branch from `main`:
   - `git checkout main`
   - `git pull origin main`
   - `git checkout -b hotfix/<short-name>`

2. Fix + commit + push, then open PR to:
- `main` (required)
- and also back into `develop` (required) to keep branches in sync

---

## Code quality
- Keep code readable and consistent
- Add/update tests when changing behavior
- Update docs when behavior or usage changes
- Avoid mixing refactors with feature changes in the same PR