#!/usr/bin/env bash
# Repeatedly launches a fresh, isolated `claude` agent process. Each invocation
# has zero memory of the last — AGENT_STATE.md is the only thing that carries
# forward. Stops when the agent itself marks Status as DONE or BLOCKED.
set -uo pipefail

PROMPT_FILE="${PROMPT_FILE:-ralph-local-prompt.txt}"
STATE_FILE="${STATE_FILE:-AGENT_STATE.md}"
LOG_DIR="${LOG_DIR:-ralph-logs}"
MAX_ITERATIONS="${MAX_ITERATIONS:-100}"   # sanity backstop, not a real budget

mkdir -p "$LOG_DIR"

for i in $(seq 1 "$MAX_ITERATIONS"); do
  ts() { date '+%Y-%m-%d %H:%M:%S'; }
  echo "[$(ts)] iteration $i: launching fresh agent"

  claude -p "$(cat "$PROMPT_FILE")" \
    --dangerously-skip-permissions \
    > "$LOG_DIR/iter-$i.log" 2>&1

  status=$(awk '/^## Status/{getline; print; exit}' "$STATE_FILE" 2>/dev/null | tr -d '[:space:]')
  echo "[$(ts)] iteration $i: finished, status=${status:-UNKNOWN}"

  if [ "$status" = "DONE" ] || [ "$status" = "BLOCKED" ]; then
    echo "Stopping — mission reached status $status. See $STATE_FILE for the final summary."
    exit 0
  fi

  sleep 5
done

echo "Hit MAX_ITERATIONS ($MAX_ITERATIONS) without reaching DONE/BLOCKED — check $STATE_FILE, this is likely a bug in the prompt or task list, not real progress."
exit 1
