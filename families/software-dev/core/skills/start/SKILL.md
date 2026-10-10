---
name: start
description: Start a new software-dev task with agentflow. Use when the person wants to begin a feature, bugfix or hotfix and no task is active. Sets up the workspace if needed, creates the gitflow branch and runs the confirm step.
---
# Start a task

Use `agentflow` for everything below. Never create or edit files under `.agentflow/` by hand.

Run every `agentflow` command on its own, as a single command line. Never join commands with `&&`, `;` or `|`.

You never push, merge or open a pull request; that is the person's job.

1. Run `agentflow status`.
   - If it says there is no workspace, set one up from the project root (a git repository with `main` and `develop` branches). Run `agentflow init --workflow <path to this plugin's workflow.yaml>`.
     The file is `workflow.yaml` in the root of the dev-core plugin. In Claude Code that is `${CLAUDE_PLUGIN_ROOT}/workflow.yaml`; in Antigravity it is under `~/.gemini/antigravity-cli/plugins/dev-core/`. If the path is not filled in, search for a `dev-core/workflow.yaml` under `~/.claude/plugins` or that Antigravity folder.
   - If a task is already active, do not start another: use the continue skill, or ask the person whether to cancel it (`agentflow task cancel`).
2. Ask the person for a short title and the type: `feature`, `bugfix` (both branch from `develop`) or `hotfix` (from `main`). Infer them from the request when it is obvious.
3. The working tree must be clean. If `agentflow` says it is not, show the person what is uncommitted and ask what to do; do not discard anything.
4. Run `agentflow task new "<title>" --type <type>`. It creates the branch `<type>/T-001-<slug>` and switches to it. If it says the previous task has no approval tag, tell the person: they run `agentflow task seal <id>` themselves.
5. Carry on with the continue skill. It runs the **confirm** step with the orchestrator agent and stops at the person's approval; after the approval it keeps going by itself.
