---
name: ralph-local
description: Generate a local, no-cloud autonomous work-loop pair (a per-task prompt + a bash wrapper script) for a given mission - each logical unit of work (or each failed attempt, up to a cap) hands off to a brand-new agent process with a fresh context window. Invoke as /ralph-local <mission description>. Use when the user wants a "ralph wiggum" style loop that runs on their own machine (no /schedule cloud routine) and wants a fresh agent per task/failure rather than one long session looping internally.
user-invocable: true
---

# ralph-local

This skill produces TWO deliverables, as files: a per-invocation prompt and a
bash wrapper script. Together they implement an autonomous work loop that runs
entirely on the user's own machine (they are responsible for keeping it awake,
e.g. via `caffeinate` - don't set that up yourself unless asked). Unlike the
`ralph` skill (which produces a single prompt that loops internally until the
whole mission is done, meant for a `/schedule` cloud routine or similar), this
variant does **exactly one task per process invocation** and then exits - the
wrapper script relaunches a fresh `claude` process for the next task. This
gives every logical unit of work (and every retry after a failure) a clean
context window, which is the whole point of this variant.

## What to do

1. Read the mission from the skill's args. If missing or too thin to act on,
   ask one short question to get a one-paragraph mission statement covering
   the goal and what "done" looks like - don't guess at something this
   consequential.
2. Also check if the user specified a failure cap (how many fresh-agent
   attempts a single task gets before it's marked blocked). Default to 3 if
   not specified.
3. Write two files into the user's current project (ask where if ambiguous,
   e.g. a `ralph/` subdirectory):
   - a prompt file (e.g. `ralph-local-prompt.txt`) using the PROMPT TEMPLATE
     below, with `{{MISSION}}` and `{{N}}` filled in, and `{{OPTIONAL BOUNDARY}}`
     removed unless the user gave a concrete off-limits area.
   - a wrapper script (e.g. `ralph-loop.sh`) using the SCRIPT TEMPLATE below,
     unchanged (it's already parameterized via env vars, nothing to fill in).
4. Tell the user how to run it (`chmod +x ralph-loop.sh && ./ralph-loop.sh`
   from the directory containing both files) and flag the two real risks
   plainly, don't bury them:
   - `--dangerously-skip-permissions` is required for unattended operation but
     removes the approval safety net entirely - recommend a dedicated branch,
     never `main`, and scoping the mission to a subdirectory where reasonable.
   - CLI flag names drift between Claude Code versions - tell them to confirm
     the skip-permissions flag with `claude --help` before trusting the script.
5. Do not start executing the mission yourself in this session - this skill's
   job ends at generating the two files.

## PROMPT TEMPLATE (write to the prompt file)

You are one of many independent agent sessions working on the same mission over time. You have no memory of any prior session except what is written in AGENT_STATE.md. No human is available to answer questions or approve actions. Do not pause to ask questions — make the most reasonable decision yourself and record it.

MISSION
{{MISSION}}

FAILURE CAP
{{N}} — the number of separate fresh-agent attempts a single task gets before it is marked blocked and skipped by all future sessions.

STATE FILE
Read `AGENT_STATE.md` in the current working directory before doing anything else.

If it doesn't exist, create it with this structure, seeded from the mission (break the mission into a concrete task checklist):

## Status
IN_PROGRESS

## Mission
{{MISSION}}

## Task List
- [ ] task 1
- [ ] task 2

## Log
(empty)

## Failure Tracker
(empty)

## Final Summary
(empty)

If `## Status` is already `DONE` or `BLOCKED`, do nothing else — the mission is already finished or fully stuck. Do not touch anything. End the session immediately.

YOUR JOB THIS SESSION — EXACTLY ONE UNIT OF WORK

1. Look at the Task List. If every task is checked off or marked `blocked`:
   - Set `## Status` to `DONE` if all tasks are checked off, or `BLOCKED` if any remain unchecked-but-blocked with none actionable.
   - Write the `## Final Summary` section: what was accomplished, what's blocked and why (per task), what remains, and one recommended next step for a human.
   - End the session now. Do not do anything further.

2. Otherwise, pick the next unchecked, unblocked task and work on ONLY that one task:
   - Inspect the actual environment first — don't assume a language, framework, test runner, or version control system. Look at what's actually there.
   - Make the smallest change that completes the task.
   - Verify using whatever validation mechanism actually exists here (tests, build, lint, type check, manual execution). If none exists, verify by careful re-reading and say so in the log.
   - On success: persist the work using whatever mechanism is native to this environment (commit if version control is present, save otherwise), check the task off, reset that task's failure count to 0 in the Failure Tracker, append one Log entry describing what you did.
   - On failure: undo or isolate the change so it doesn't leave things broken, increment that task's failure count in the Failure Tracker, append one Log entry with exactly what you tried and why it failed.
     - If the failure count for this task is now >= the FAILURE CAP above: mark the task `blocked` in the Task List with a one-line reason. Leave `## Status` as `IN_PROGRESS` if other unblocked tasks remain, or `BLOCKED` if this was the last one.
     - If under the cap: leave the task unchecked and not blocked — a future fresh session will retry it.

3. Regardless of success or failure, after handling that ONE task: stop. Do not start a second task in this session, even if you have remaining capacity. End the session now so the next invocation starts with a clean context window.

BOUNDARIES
- Never take an action that is irreversible and outside the explicit scope of the mission (deleting unrelated data, force-pushing over others' work, touching systems not named in the mission). Mark it `blocked — needs a human` in the Failure Tracker instead.
- {{OPTIONAL BOUNDARY}}

Do not report progress anywhere except AGENT_STATE.md — no chat messages, no emails, no other notifications.

## SCRIPT TEMPLATE (write to the wrapper script, verbatim, no substitution needed)

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
