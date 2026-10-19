# Research checklist

Answer each item from the repository itself: read manifests, configs, docs, routes, tests, CI. Never guess a port, selector or route. Where the repo does not say, record "unknown" and ask the user (one `ask_user` form for all unknowns), or pick the safest default and say so in the report.

Field names are TypeScript (`proof/app.ts`). Python kit (`proof/app.py`): `APP.source_paths`, `StartConfig(command, args, env, cwd, prerequisites, ready, timeout_s)`, `ApiConfig(discover, probe)`, `WebConfig(settle, snapshot)`; hooks are synchronous callables. Start scripts also come from `pyproject.toml` scripts, `Makefile`, `manage.py`, `uvicorn`/`flask` entry points.

## 1. Start and stop (fills `APP.url`, `APP.start`)

- [ ] The dev or start script: `package.json` scripts (`dev`, `start`, `serve`), `Procfile`, `docker-compose.yml`, `README`/`CONTRIBUTING`. Pick the command a developer runs locally, not a production build.
- [ ] The port and base URL (config files, `.env.example`, framework defaults). Does an env var set it (`PORT`)? Pass it in `APP.start.env`.
- [ ] A ready signal stronger than "the port answers": a health route, a seeded list, a first render. Put it in `APP.start.ready`.
- [ ] Prerequisites: a database or container runtime, a required SDK or CLI version (`.nvmrc`, `global.json`, `engines`), env files, migrations, seed command. Anything that must exist before start goes in `APP.start.prerequisites` (throw an actionable message) or is documented in the map.
- [ ] Auth: is the surface under test reachable anonymously? If login is required, note it as out of scope or find a documented test account.
- [ ] First-start cost: a cold start can take minutes; set `timeoutMs`.

## 2. Revision (fills `APP.sourcePaths`)

- [ ] The folders whose edits change the running app: the web app and the API it reads. Exclude tests, docs, `proof/`, `node_modules`, build output. Prefer a few specific folders to `.`.
- [ ] The repo has at least one commit (the revision needs `HEAD`).

## 3. Web surface (only if `web` is chosen)

- [ ] Routes: the router config, pages folder, or sitemap. Pick stable, anonymous, read-only pages.
- [ ] Stable selectors, in this order: role/label/text a user sees, `data-testid`, a semantic class. Never positional or generated class names. Existing e2e tests (`e2e/`, `tests/`, `cypress/`, `playwright.config.*`) show which selectors the team already trusts.
- [ ] What "rendered" means: loading spinners, streaming or client-side hydration. Put the wait in `APP.web.settle`.
- [ ] Console errors expected in a healthy app (so `pageErrors` is meaningful).

## 4. API surface (only if `api` is chosen)

- [ ] The base URL and prefix: same origin as the web app, a proxy, or a separate port. If discovered at runtime (service discovery, random ports) write `APP.api.discover`.
- [ ] The routes: OpenAPI/Swagger file, controllers, route files, `.http` files, README. Pick read-only `GET` routes.
- [ ] Wire details an adapter must hide: versioning (header or `api-version` query), 0- vs 1-based paging, ids vs names, envelope shapes, auth headers.
- [ ] A health route for `APP.api.probe`; otherwise any answer below 500 counts.
- [ ] Error contract: the status for a missing resource (404) and for invalid input (400 or 422).

## 5. Test data

- [ ] Is there a seed (SQL, JSON, fixtures, a seed script)? Which numbers are stable (counts, names, ids)? Where is the seed file (cite it in hints)?
- [ ] Is state shared or mutable between runs? A proof must be repeatable on the same data.

## 6. Existing coverage as hints

- [ ] Read e2e and API tests for the behaviors the team already treats as important; lift contracts, not code.
- [ ] Note CI's way of starting the app: it is usually the most reliable start recipe.

## Output of the research

A short list per item above: value, source (file:line), and confidence. Use it to fill `proof/app.ts`, to pre-fill the case menu, and to write `verify-mole` (`TODO(proof)` markers).
