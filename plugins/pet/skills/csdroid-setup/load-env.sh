# Load CSDROID_HARNESS_ROOT and CSDROID_WORKSPACE_ROOT into the current shell.
# SOURCE this file, do not execute it: `. <skill-dir>/load-env.sh`
# Sources .csdroid.env if present; otherwise detects inline as a fallback so a
# skill still runs standalone (mirrors detect-env.sh without writing the file).

__csdroid_env_file="$(git rev-parse --show-toplevel)/.csdroid.env"

if [ -f "$__csdroid_env_file" ]; then
  # shellcheck disable=SC1090
  . "$__csdroid_env_file"
else
  CSDROID_HARNESS_ROOT=$(cd "$(git rev-parse --git-common-dir)/.." && pwd)
  while __csdroid_parent=$(cd "$CSDROID_HARNESS_ROOT/.." && git rev-parse --show-toplevel 2>/dev/null); do
    CSDROID_HARNESS_ROOT=$__csdroid_parent
  done
  if [ -d "$CSDROID_HARNESS_ROOT/workspace" ] && \
     git -C "$CSDROID_HARNESS_ROOT/workspace" rev-parse --show-toplevel >/dev/null 2>&1; then
    CSDROID_WORKSPACE_ROOT=$(cd "$CSDROID_HARNESS_ROOT/workspace" && git rev-parse --show-toplevel)
  else
    CSDROID_WORKSPACE_ROOT=$CSDROID_HARNESS_ROOT
  fi
  export CSDROID_HARNESS_ROOT CSDROID_WORKSPACE_ROOT
  unset __csdroid_parent
fi

unset __csdroid_env_file
