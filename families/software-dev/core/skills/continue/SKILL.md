---
name: continue
description: Continue the active software-dev task with agentflow. Use when a task exists and the person asks to carry on, resume after a break, or do the next step. Runs steps one after another with the right role until a step needs a person.
---
# Continue the active task

Use `agentflow` for everything below. Never create or edit files under `.agentflow/` by hand.

Run every `agentflow` command on its own, as a single command line. Never join commands with `&&`, `;` or `|`. To save a report, send the Markdown on standard input with a quoted heredoc (`<<'EOF'`), not a pipe.

You never push, merge or open a pull request; that is the person's job.

## The loop

Repeat these until one of the stop conditions below:

1. Run `agentflow next`. Its first word tells you what to do:
   - `start_task`: there is no active task; use the start skill.
   - `await_approval`: a person has to approve the step. Tell them which step and where its report is, then stop. The approve skill handles it. Never approve a step yourself.
   - `blocked`: the task failed too many times. Show the person the latest reports in `.agentflow/tasks/<task>/reports/`, say the options (approve to resume, or cancel) and stop.
   - `continue`: work on the named step, as below, then go back to 1.
2. Make sure you are on the task's branch (shown by `agentflow status`). If not, switch with `git switch <branch>`.
3. Hand the step to the role that owns it, in Claude Code by calling the agent of that name and in Antigravity by using the agent of the same name:

   | Step | Role | What it produces |
   |---|---|---|
   | confirm | `orchestrator` | confirmation report |
   | plan | `planner` | plan report that passes `agentflow plan check` |
   | implement | see below | code, commits through `agentflow commit`, summary report |
   | test | `tester` | tests (test directories only), test report |
   | security | `security` | scan results and security report |
   | review | `reviewer` | review report |

   The role saves its report with `agentflow report --step <step>` and records the result with `agentflow task advance --result pass` (or `fail`).

   **implement:** read the approved plan (`.agentflow/tasks/<task>/reports/plan.md`). Take its items in order and give each one to the agent named in its `role:` line (`implementer` for the usual code; plugins add roles of their own). Tell the agent the item code, so it commits with `--item <code>`. Give the last item's agent the extra job of saving the implement summary and recording the step as passed. If a skill of an installed plugin fits an item, tell the agent to use it.
4. After the role finishes, run `agentflow status`. A pass that needs no approval means: go back to 1 straight away. Do not ask the person whether to continue.

## Stop conditions

Stop and tell the person where things stand only when:

- the next action is `await_approval` or `blocked`;
- a question is genuinely theirs to decide (do not guess);
- a command was refused for a reason you cannot fix (for example a gate or an unavailable container engine);
- the task is done. Say that `.agentflow/tasks/<task>/summary.md` has the summary and that the approval tag `agentflow/<task>/approved` is on the task branch. Merging and pushing are the person's job.

A failing test, security or review step sends the task back to `implement` by itself; after 3 rounds the task is blocked.

Only the implementer-type roles change project code, each only for its own plan items.
