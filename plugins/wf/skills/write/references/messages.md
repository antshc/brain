# Messages: chat, email, and issue comments

- Put the bottom line or the ask in the first line.
- Ask for one thing per message. When several answers are needed, number the questions.
- Keep chat messages to 1 to 5 lines. Move detail into a linked document or issue.
- Skip headings in short messages. Use a short list only for parallel items.
- Match the register of the thread. Drop greetings and sign-offs the thread does not use.
- Name the decision, the owner, and the date when the message asks for action.
- Put links and logs last, each with a word that says what it holds.

## Worked example

Before:

> Hi team! Hope everyone is doing well. I wanted to give a quick update on the migration. We ran into some issues with the schema yesterday, which we've been looking into, and it seems like the column rename is causing the build to fail. Could someone from data take a look when they get a chance? Thanks so much!

After:

> Can someone from data review the `orders.total` rename by Thursday? It fails the build: [CI run 4812](https://ci.example.com/runs/4812).
