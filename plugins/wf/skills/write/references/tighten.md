# Tighten

Edit the supplied prose for its audience: cut words, not information, and remove AI tells. Keep the author's meaning, every fact, condition, number and caveat, the level of certainty, the intended tone and protected text. Keep sentences grammatical; tightened text is still written for people.

**Formatting is structure, not wording.** Keep every heading, its level and order, every list, table, row, column, code fence, link, template section and structural marker. Edit only the words inside them. Remove a list item or table row only when it duplicates another.

## Cut what the reader already has

Delete sentences that restate a heading, the previous sentence or a later summary. Delete announcements of what the text is about to say. Keep one statement of each point, in its most useful place.

| Pattern | Before | After |
|---|---|---|
| Restated heading | `## Retries` The following section describes how retries work. The worker retries a failed write once. | `## Retries` The worker retries a failed write once. |
| Restated point | The cache expires after 10 minutes. After 10 minutes, cached entries are no longer valid. | The cache expires after 10 minutes. |
| Recap | In summary, the worker retries once and then records the batch ID. | Delete when the paragraph above already says it. |

## Use the short form

Turn noun phrases back into verbs. Drop words implied by their partner. Replace multi-word phrases with one word.

| Pattern | Before | After |
|---|---|---|
| Nominalization | The service performs validation of the token. | The service validates the token. |
| Redundant pair | Each and every request must include a valid and correct token. | Every request must include a valid token. |
| Implied word | The batch is retried again at a later point in time. | The batch is retried later. |
| Wordy phrase | In order to export the file, due to the fact that the job is running, … | To export the file, because the job is running, … |
| Empty subject | There are three workers that read from the queue. | Three workers read from the queue. |

## Merge what shares a subject

Combine consecutive sentences with the same actor or object into one sentence when it stays easy to parse. Split again if the merged sentence needs a second reading.

| Pattern | Before | After |
|---|---|---|
| Same actor | The worker reads the batch. The worker writes it to storage. The worker then deletes the message. | The worker reads the batch, writes it to storage and deletes the message. |
| Same object | The token expires after one hour. The token cannot be renewed. | The token expires after one hour and cannot be renewed. |

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

Remove empty greetings, praise, canned closings and padding. Keep meaningful qualifiers; remove repetitive hedging. Check natural rhythm, then compare against the input: every fact, condition and caveat survives, and no claim became stronger or weaker.

| Pattern | Before | After |
|---|---|---|
| Flattery and canned reply | Brilliant catch! The timestamp is in UTC. Happy to help! | The timestamp is in UTC. |
| Padding | As a point of clarification, the API accepts one token per request. | The API accepts one token per request. |
| Stacked uncertainty | The worker might possibly skip a batch if its lease expires. | The worker might skip a batch if its lease expires. |
