# Answer shapes

Fill the shape for the routed branch. Drop any line the question does not need.

## Test it

```
**What you're checking:** {{the behaviour, in product words}}

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

```
**{{METHOD}} {{full path}}** — {{what it does}}

- **Base URL:** {{per environment, or where to get it}}
- **Auth:** {{header}} — {{how to get the token}}

{{curl or raw HTTP snippet with real field names and sample values}}

**Fields**
| Field | Required | Allowed values | Means |
|---|---|---|---|

**Success:** {{status}} — {{response shape with a sample value}}

**Errors**
| Status | Happens when |
|---|---|
```

## Change the data

Prefer the front door: when an endpoint writes the same record, give that request instead of a direct write, and say why.

```
**Where it lives:** {{store}} → {{table or collection}} — {{what one record represents}}

**Find your record by:** {{key fields}}, e.g. {{real example values}}

**Change it**
1. {{console or CLI step, one action per step}}

{{CLI command, or the console fields and the values to type}}

**Check it worked:** {{what to re-read, and what it should now say}}
**Put it back:** {{the reverse change}}
**Watch out:** {{what the change knocks over — cached copies, downstream records, a sync job}}
```

## Find the setting

```
| Environment | File | Setting | Controls | Useful for testing |
|---|---|---|---|---|

**To {{the tester's goal}}:** in {{file}}, set {{setting}} to {{value}} (currently {{current value}}).

- **Takes effect:** {{immediately / on restart / on redeploy}}
- **Put it back:** {{original value}}
- **Who applies it:** {{tester locally / a dev / devops}} — the file is unchanged.
```
