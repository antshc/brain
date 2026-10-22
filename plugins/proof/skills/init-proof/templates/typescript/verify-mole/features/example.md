# example (placeholder)

A smoke check that the app answers on each surface. Replace it with real features, or keep it as the first gate.

## Sub-features

- `app-answers` — The app answers on every surface.

## How to get to it (user POV)

<!-- surface: web -->
Open the app's home page.
<!-- /surface: web -->
<!-- surface: api -->
Send a request to the API's root.
<!-- /surface: api -->

## Driving it with Mole

<!-- surface: web -->
**(app-answers | web):** **Given** the app is running; **When** a visitor opens the home page; **Then** the page shows a heading. **Proof:** the page shows a heading (DOM assertion).

<!-- /surface: web -->
<!-- surface: api -->
**(app-answers | api):** **Given** the API is running; **When** a client requests its root; **Then** the API answers without a server error. **Proof:** the API answers below 500 (API response).

<!-- /surface: api -->
## Gotchas

- A stale build: `{{MOLE}} doctor` says STALE when the source moved past the running app.
