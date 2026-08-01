# Ralph owns a portable agent pipeline

Ralph packages and directly orchestrates the named Codey and Chorey agents as one installed workflow. Codey implements each task, then Chorey reviews the uncommitted changes for refactoring candidates, applies justified fixes, and reruns the feedback loop before Ralph commits the result.

Codey and Chorey execute code, Git, build, test, and exploration commands in the directory from which Ralph launches them. Neither agent receives or discovers a `WORKTREE_PATH`; callers establish the execution location before invocation, and each agent treats that invocation directory as its workspace.

`ralph-init` resolves the Source Repository with the same fail-closed topology contract as worktree setup, infers and confirms one primary senior-developer persona from repository evidence, installs Ralph skills, and writes its delimited expertise, working-style, and skill-use configuration directly into Codey and Chorey. `ralph-init` also creates `VERIFY.md`; `ralph-verify` reads that required guidance directly and has no fallback path.

The `/to-codey` and `/to-chorey` skills run the `codey` and `chorey` agents respectively. Codey and Chorey remain independently selectable and directly runnable without either routing skill.