# Ralph agents are run-location-agnostic

Codey and Chorey execute code, Git, build, test, and exploration commands in the directory from which Ralph launches them. Neither agent receives or discovers a `WORKTREE_PATH`; callers establish the execution location before invocation, and each agent treats that invocation directory as its workspace.

The agents do not resolve repository-location declarations. Coding, verification, refactoring, and Gotchas guidance remain skill-owned references beside their consuming skills, with technology-agnostic fallbacks when optional guidance is absent.