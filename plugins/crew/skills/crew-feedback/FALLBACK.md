# Verify Fallback

Used by `crew-feedback` Step 1 when `VERIFY_PATH` is unresolved (no `VERIFY.md` found). Never hardcodes a language or toolchain — discover it per repo.

- **LSP diagnostics**: run `get diagnostics` on all changed files.
- **Discover the toolchain**: read `HARNESS_REPO_PATH/README.md` for documented build/verify instructions, and explore the repo's own project/config files (manifests, build files, lockfiles) to identify the build and test tooling in use. A passing `get diagnostics` does NOT replace a build — many analyzers only fire during a real build.
- **Build**: run the discovered build command for each unique affected Module (do not build the same Module twice).
- **Tests**: run the discovered test command for each unique affected Verification counterpart, scoped to the classes/specs that correspond to changed files in that Verification counterpart's scope.
