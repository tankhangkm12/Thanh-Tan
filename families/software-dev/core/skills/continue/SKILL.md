---
name: continue
description: Continue the active software-dev task with agentflow. Use when a task exists and the person asks to carry on, resume after a break, or do the next step. Runs the current step with the right role and records the result.
---
# Continue the active task

Use `agentflow` for everything below. Never create or edit files under `.agentflow/` by hand.

1. Run `agentflow next` (and `agentflow status` for detail). Read the output:
   - `start_task`: there is no active task; use the start skill.
   - `await_approval`: a person has to approve the step. Tell them and stop; the approve skill handles it. Do not approve it yourself.
   - `blocked`: the task failed too many times. Show the person the latest reports in `.agentflow/tasks/<task>/reports/`, tell them the options (approve to resume, or cancel) and stop.
   - `continue`: work on the named step, as below.
2. Make sure you are on the task's branch (shown by `agentflow status`). If not, switch to it with `git switch <branch>`.
3. Hand the step to the role that owns it:

   | Step | Role | What it produces |
   |---|---|---|
   | confirm | `orchestrator` | confirmation report |
   | plan | `planner` | plan report |
   | implement | `implementer` | code, commits through `agentflow commit`, summary report |
   | test | `tester` | tests (test directories only), test report |
   | security | `security` | security report |
   | review | `reviewer` | review report |

   In Claude Code call the agent by that name; in Antigravity use the agent of the same name. The role saves its report with `agentflow report --step <step>` and records the result with `agentflow task advance --result pass|fail`.
4. After the role finishes, run `agentflow status` again and tell the person where the task stands. A failing test, security or review step sends the task back to `implement` automatically; after 3 rounds it becomes blocked.
5. Stop whenever the next action needs a person (approval, blocked, a question).

Only the implementer changes project code. Never run `git push`, and never commit on `main` or `develop`.
