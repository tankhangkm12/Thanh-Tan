---
name: status
description: Show where the software-dev workflow stands with agentflow. Use when the person asks about progress, the current step, the active task or what happens next. Read-only.
---
# Show the workflow status

1. Run `agentflow status` and, for the next action only, `agentflow next`.
2. Report in a few lines: the active task (id, title, branch), the current step and its role, the state (in progress, waiting for approval, blocked), the rework rounds used (for example 1/3), and what comes next.
3. If the person wants detail, read the reports in `.agentflow/tasks/<task>/reports/` and any file in `.agentflow/decisions/`. You may read `.agentflow/STATE.md`.
4. If `agentflow` says there is no workspace, say so and point to the start skill.

This skill only reads. Do not change task state and never edit files under `.agentflow/`.
