# glow-bruno

Bruno [OpenCollection](https://docs.usebruno.com/opencollection-yaml/overview) workspace for the Glow microservices API.

## Setup (once after clone)

Requires [Git](https://git-scm.com/) and [Python 3](https://www.python.org/downloads/).

```bash
cd glow-bruno
./.githooks/install.sh
```

This configures a **git clean filter** (personal data stripped on `git add`) and **pre-commit** (gitleaks backstop). On Windows, run from **Git Bash**.

Optional: install pre-commit first (`brew install pre-commit` or `pip install pre-commit`) so `install.sh` can register commit hooks too.

## Open in Bruno

1. Install [Bruno](https://www.usebruno.com/) 3.0+ (YAML collections).
2. Open `workspace.yml` in this repo.
3. Select an environment: **local**, **staging**, or **prod**.

Request bodies and entity IDs live in each request file — not in environment variables.

## Authentication

The collection uses **OAuth 2.0 — Password Credentials** against Keycloak (`glow-realm`, client `glow-frontend`). Protected requests inherit it and **auto-fetch** a token when needed.

1. Create a user in Keycloak (`glow-realm`) and assign the **CUSTOMER** role.
2. Set `username` and `password` in your Bruno environment (local values stay on disk; the git clean filter blanks them on `git add`).
3. Run service or seed requests — no separate “get token” step.

`local.yml` may show as modified in `git status` after commit; that is expected.

## Seed data

Run requests in **seed/** in order (see [collections/glow/seed/README.md](collections/glow/seed/README.md)). Step 1 creates a restaurant; steps 2–3 add menu items for the UI.

## Editing the collection

See [AGENTS.md](AGENTS.md) for request layout conventions (agents and contributors).
