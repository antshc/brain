# example (placeholder)

A smoke check that the app answers. Replace it with real features, or keep it as the first gate. Code: `proof/features/example.py`.

## Sub-features

- smoke: the app is up and answers.

## How to get to it (user POV)

- Open the app's home page<!-- surface: web+api --> in a browser, or call its API root<!-- /surface: web+api --><!-- surface: api-only -->: call its API root<!-- /surface: api-only -->.

## Driving it with Mole

(smoke | app-answers): **Given** the app is running; **When** the user opens the app; **Then** it answers below the failure range; **Proof** the app answered (<!-- surface: web+api -->network log + API response<!-- /surface: web+api --><!-- surface: web-only -->network log<!-- /surface: web-only --><!-- surface: api-only -->API response<!-- /surface: api-only -->).

Run it: `{{MOLE}} run example`. Look at it: `{{MOLE}} snapshot`<!-- surface: api -->, `{{MOLE}} api get /`<!-- /surface: api -->.

## Gotchas

- A stale build: `{{MOLE}} doctor` says STALE when the source moved past the running app.
