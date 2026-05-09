# Interface Design for Testability

Good interfaces make testing natural:

1. **Accept dependencies, don't create them**

   Inject dependencies via the constructor; never use `new` - that makes the dependency impossible to replace in tests

2. **Return results, don't produce side effects**
   Prefer queries that return a value (CQS) over `void` methods that mutate state.

3. **Small surface area**
   - Fewer methods = fewer tests needed
   - Fewer params = simpler test setup
