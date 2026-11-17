# Unslop

Edit the supplied prose for its audience. Keep the author's meaning, level of certainty, and intended tone.

## Ground each claim

Name attribution sources. Remove unsupported assertions and trailing claims of unestablished effects. State the actor, action and observable result. Close with the actual finding, decision or next action.

| Pattern | Before | After |
|---|---|---|
| Unsupported effect | The worker saves the batch ID after each write, guaranteeing recovery from any failure. | The worker saves the batch ID after each write. |
| Vague attribution | Engineers reported a timeout. The network team's incident report is the source. | The network team's incident report documents a timeout. |
| Vague benefit | Resume is effortless because the worker starts at the last saved batch. | The worker resumes at the last saved batch. |
| Generic closing | We plan to remove the flag in version 3. The outlook is promising. | We plan to remove the flag in version 3. |

## Make the sentence easy to parse

Name the actor and use direct verbs and everyday words. Split hard-to-follow clauses. Replace vague intensifiers with available measurements. Use complete sentences instead of cryptic shorthand; keep passive when the actor is unknown or irrelevant.

| Pattern | Before | After |
|---|---|---|
| Buried actor and vague speed | The snapshot was restored rapidly by the worker in 18 seconds. | The worker restored the snapshot in 18 seconds. |
| Inflated wording | The queue constitutes the central mechanism for storing pending jobs. | The queue stores pending jobs. |
| Dense sentence | If the write fails, the worker retries once, and if the retry fails, it records the batch ID and exits. | If the write fails, the worker retries once. If the retry fails, it records the batch ID and exits. |
| Shorthand | API: missing token → HTTP 401, no session. | If the token is missing, the API returns HTTP 401 and creates no session. |

## Keep terms and structure literal

Use one name per thing. Replace unclear metaphors with actual components or operations. Group by relationships, without forcing a list length. Range endpoints need one scale; contrasts need both sides to be useful.

| Pattern | Before | After |
|---|---|---|
| Changing names for one thing | The worker claims the job. The runner renews the lease every minute. | The worker claims the job and renews the lease every minute. |
| Metaphor and flourish | The retry queue is the gatekeeper. Nothing gets through without a lease. | A job needs a lease before it leaves the retry queue. |
| Forced grouping | The release fixes login, sign-in, and file export. | The release fixes login and file export. |
| False range | The guide covers everything from access tokens to CSV export. | The guide covers access tokens and CSV export. |
| Stock contrast | The service does more than check tokens. It also records failed attempts. | The service checks tokens and records failed attempts. |

## Clear the page

Use sentence case, straight quotes and meaningful bold. Remove decorative emoji and labels repeating their sentence. Reserve colons for lists or examples; separate thoughts with grammatical periods or commas.

| Pattern | Before | After |
|---|---|---|
| Punctuation between statements | The queue is empty — the worker exits. The exit code is set: it is `0`. | The queue is empty, so the worker exits with code `0`. |
| Repeated label and excess bold | **Retries:** Retries stop after **three attempts** for **HTTP 429**. | For HTTP 429, retries stop after **three attempts**. |
| Useful label | **Lease duration:** A lease lasts 60 seconds. | **Lease duration.** The lease expires after 60 seconds. |
| Title case and decoration | `## 🔧 Restore The Snapshot` | `## Restore the snapshot` |
| Curly quotation marks | The banner says “Upload complete”. | The banner says "Upload complete". |

## Read it as the recipient

Remove empty greetings, praise, canned closings and padding. Keep meaningful qualifiers; remove repetitive hedging. Check natural rhythm, then compare facts, scope and confidence with the input.

| Pattern | Before | After |
|---|---|---|
| Flattery and canned reply | Brilliant catch! The timestamp is in UTC. Happy to help! | The timestamp is in UTC. |
| Padding | As a point of clarification, the API accepts one token per request. | The API accepts one token per request. |
| Stacked uncertainty | The worker might possibly skip a batch if its lease expires. | The worker might skip a batch if its lease expires. |
