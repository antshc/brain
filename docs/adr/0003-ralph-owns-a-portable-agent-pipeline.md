# Ralph owns a portable agent pipeline

Ralph packages and directly orchestrates the named Codey and Chorey agents as one installed workflow. Codey implements each task, then Chorey reviews the uncommitted changes for refactoring candidates, applies justified fixes, and reruns the feedback loop before Ralph commits the result.

Codey and Chorey execute code, Git, build, test, and exploration commands in the directory from which Ralph launches them. Neither agent receives or discovers a `WORKTREE_PATH`; callers establish the execution location before invocation, and each agent treats that invocation directory as its workspace.

The agents and their supporting skills carry no language- or toolchain-specific knowledge. Repository-specific coding and verification guidance lives in mutable references beside the consuming skills; when a reference is absent, the skill reports that absence and uses a bundled technology-agnostic fallback that discovers the toolchain from repository evidence.