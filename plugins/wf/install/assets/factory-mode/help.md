# Help

Use this procedure when the user asks for help or when a request has no clear route. Use the Routes table in the entry file as the source of available Factory Mode routes. Keep this procedure read-only. Load route dependencies after the user chooses a route.

## Show usage

For `help` without a request, list the routes and show one example for each. Include these invocation forms:

```text
/factory-mode <request>
/factory-mode help
/factory-mode help <request>
/factory-mode stories from <requirements or spec>
/factory-mode review https://github.com/owner/repo/pull/123
```

Done when the usage and examples are visible.

## Help with a request

1. Keep the original request. Restate the goal, problem, and smallest change that would meet the request. Done when the user can check your understanding.
2. If repo context would help select a route, use a read-only search for the owning module, tests, and relevant architecture or glossary entries. Done when you can name the area or identify what is missing.
3. Show up to three applicable routes. Rank them and give the reason, expected output, skills, required inputs, and checkpoints for each. If no route fits, state what detail would make a route applicable and ask for clarification. Done when the user can choose an applicable route or clarify the request.
4. Wait for the user's reply. On selection, return the chosen route and original request plus clarifications to the entry file. Load the chosen route only then.
