# Answer shapes

Fill the shape for the routed branch. Drop any line the question does not need.

## On the wire

Every request in every shape goes in one `http` block, **on the wire** — request, blank line, response — so the tester can read it or paste it straight into their API client:

```http
GET /api/v2/alerts?top=1000 HTTP/1.1
Host: zic.example.com
Authorization: Bearer {{token}}

HTTP/1.1 200 OK
Content-Type: application/json

{
  "alerts": [ { "...": "..." } ]
}
```

Real host, real path, real query and field names. Leave only the secret as `{{token}}`.

## In its own format

Show every record and setting **in the format the tester edits it in**, so they can paste it where it belongs — SQL for a relational store, a JSON item for DynamoDB or a document store, the file's own syntax for config. Always give the current value beside the new one.

```sql
SELECT status, plan FROM subscriptions WHERE customer_id = 'CUS-4821';

UPDATE subscriptions SET status = 'cancelled' WHERE customer_id = 'CUS-4821';
```

```json
{
  "customerId": "CUS-4821",
  "sk": "SUBSCRIPTION#2026-01",
  "status": "cancelled",
  "plan": "premium"
}
```

```json
"Alerts": {
  "PollIntervalSeconds": 5,
  "UseSandboxProvider": true
}
```

## Test it

```
**What you're checking:** {{the behaviour, in product words}}
**Where:** {{deployed environment}} — {{URL or console to reach it}}

**Set up**
1. {{test data or account state to have in place, with real values}}

**Do this**
1. {{one front-door action per step — a request, a screen step, a file drop}}

**Expect**
- {{observable outcome — status code, field value, message, record, file}}

**Where to look**
- {{where the evidence lands — response body, table or collection, log, queue, email}}

**Also worth trying**
- {{edge or negative case}} → {{what should happen}}
```

## Call it

````
**{{METHOD}} {{full path}}** — {{what it does}}

- **Host:** {{deployed environment}} → {{host}}
- **Auth:** {{header}} — {{how to get the token}}

```http
{{the exchange, on the wire}}
```

**Fields**
| Field | Required | Allowed values | Means |
|---|---|---|---|

**Errors**
| Status | Happens when |
|---|---|
````

## Change the data

Prefer the front door: when an endpoint writes the same record, give that request instead of a direct write, and say why.

````
**Where it lives:** {{deployed environment}} → {{store}} → {{table or collection}} — {{what one record represents}}

**Find your record**
```{{sql | json}}
{{the lookup, in the store's own format, with real key values}}
```

**Change it**
```{{sql | json}}
{{the write, in the store's own format}}
```

**Check it worked:** {{what to re-read, and what it should now say}}
**Put it back:** {{the reverse statement or the original item}}
**Watch out:** {{what the change knocks over — cached copies, downstream records, a sync job}}
````

## Find the setting

These are the settings a tester can set to make the application behave differently — flags, toggles, thresholds, timeouts, sandbox and stub modes.

````
**Settings you can change in {{deployed environment}}** — {{config file path}}

| Setting | Now | Set to | What it makes the application do |
|---|---|---|---|

**To {{the tester's goal}}**
```{{json | ini | env}}
{{the fragment exactly as it appears in the file, with the new value in place}}
```

- **Takes effect:** {{immediately / on restart / on redeploy}}
- **Put it back:** {{original value}}
- **Who applies it in {{environment}}:** {{the tester / a dev / devops}} — the file is unchanged.
````
