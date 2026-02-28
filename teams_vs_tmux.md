# Claude Code Agent Teams vs DIY tmux Multi-Session Orchestration

A comparative analysis of two approaches to running multiple Claude Code
instances in parallel: the built-in **Agent Teams** feature (experimental)
and a **DIY tmux-based** approach where sessions coordinate through
`tmux send-keys`, shared files, and pane observation.

## Overview

### Agent Teams (Built-in)

Agent Teams is an experimental Claude Code feature that coordinates multiple
independent Claude Code instances as a team. A **team lead** session spawns
**teammates**, each running in its own context window. Agents communicate
through a built-in **mailbox** and coordinate via a **shared task list** with
automatic dependency management.

Enable with:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### DIY tmux Multi-Session

A manual orchestration pattern where you launch multiple Claude Code sessions
in separate tmux panes or windows. Sessions can communicate by:

- **`tmux send-keys`** to inject text/commands into other panes
- **`tmux capture-pane`** to read another pane's visible output
- **Shared files** (lock files, JSON registries, coordination directories)
- **Git worktrees** for file-level isolation between sessions

Community projects like
[claude_code_agent_farm](https://github.com/Dicklesworthstone/claude_code_agent_farm)
formalize these patterns into orchestration frameworks.

---

## Strengths

### Agent Teams Strengths

| Strength | Details |
|:---------|:--------|
| **Native integration** | Built into Claude Code; no external scripts or frameworks needed |
| **Structured messaging** | First-class mailbox system for direct, reliable inter-agent messaging |
| **Shared task list** | Agents see task status, claim work, and track dependencies automatically |
| **Automatic dependency resolution** | Completing a task auto-unblocks dependent tasks without manual intervention |
| **File-lock-based task claiming** | Prevents race conditions when multiple agents try to claim the same task |
| **Display modes** | In-process mode (any terminal) or split-pane mode (tmux/iTerm2) |
| **Direct teammate interaction** | Shift+Down to cycle teammates, or click panes in split mode |
| **Plan approval workflow** | Teammates can work in read-only plan mode until the lead approves |
| **Hooks support** | `TeammateIdle` and `TaskCompleted` hooks enforce quality gates |
| **CLAUDE.md inheritance** | Teammates automatically load project context, MCP servers, and skills |
| **Graceful lifecycle** | Built-in shutdown requests, team cleanup, and idle notifications |

### DIY tmux Strengths

| Strength | Details |
|:---------|:--------|
| **Full control** | You define the coordination protocol, communication format, and workflow |
| **No experimental flag** | Works with stable Claude Code features; no dependency on experimental APIs |
| **Scalability** | Community frameworks run 20+ agents; no artificial limits on team size |
| **Custom coordination** | Design lock protocols, registries, and workflows specific to your needs |
| **Session independence** | Each session is fully isolated; crash of one doesn't affect others |
| **Persistence** | tmux sessions survive terminal disconnects; work continues unattended |
| **Observable** | `tmux capture-pane` lets agents or humans inspect any session's output |
| **Cross-project** | Easily coordinate work across multiple repositories using different panes |
| **Flexible communication** | Mix and match: send-keys, shared files, pipes, sockets, or APIs |
| **Technology agnostic** | Could coordinate Claude with other tools, scripts, or even non-Claude agents |

---

## Weaknesses

### Agent Teams Weaknesses

| Weakness | Details |
|:---------|:--------|
| **Experimental status** | Disabled by default; known limitations around session resumption and shutdown |
| **No session resumption** | `/resume` and `/rewind` don't restore in-process teammates; lead may message dead agents |
| **High token cost** | Each teammate is a full Claude instance with its own context window |
| **One team per session** | Cannot manage multiple teams from a single lead |
| **No nested teams** | Teammates cannot spawn their own sub-teams |
| **Fixed leadership** | The lead session cannot be transferred or promoted |
| **Task status can lag** | Teammates sometimes fail to mark tasks as completed, blocking dependents |
| **Shutdown can be slow** | Teammates must finish current request/tool call before stopping |
| **Split panes limited** | Not supported in VS Code integrated terminal, Windows Terminal, or Ghostty |
| **Permissions inflexible** | All teammates inherit lead's permissions at spawn; can't set per-teammate at creation |
| **Lead context not shared** | Teammates don't inherit the lead's conversation history, only the spawn prompt |

### DIY tmux Weaknesses

| Weakness | Details |
|:---------|:--------|
| **No native messaging** | Must build communication via send-keys, files, or custom protocols |
| **Fragile coordination** | send-keys can be unreliable (timing issues, pane focus, buffering) |
| **Manual task management** | No built-in shared task list; must implement with files or databases |
| **No dependency resolution** | Must manually track and enforce task dependencies |
| **Race conditions** | Without careful locking, agents can step on each other's work |
| **Complex setup** | Requires scripting tmux layout, session management, and agent spawning |
| **No structured discovery** | Agents can't natively discover teammates or their roles |
| **Maintenance burden** | Custom orchestration scripts need ongoing maintenance |
| **Pane observation is lossy** | `capture-pane` only sees visible buffer; scrollback and tool use details are lost |
| **No graceful lifecycle** | Must implement your own shutdown, health checks, and cleanup logic |

---

## Capability Gap Analysis

| Capability | Agent Teams | DIY tmux | Gap |
|:-----------|:----------:|:--------:|:----|
| **Inter-agent messaging** | Native mailbox with direct and broadcast | `tmux send-keys` + shared files | Teams has reliable, structured messaging; tmux is ad-hoc and fragile |
| **Task coordination** | Shared task list with states and dependencies | Manual (files, JSON registries) | Teams automates what tmux requires custom implementation for |
| **Dependency management** | Automatic unblocking on task completion | Must be hand-coded | Significant gap; tmux approach requires custom dependency graph logic |
| **Agent discovery** | Teammates auto-discover via team config | Must read tmux session/pane lists | Teams is native; tmux requires parsing `tmux list-panes` output |
| **Session resumption** | Broken (known limitation) | tmux sessions persist natively | tmux is **better** here; sessions survive disconnects |
| **Scalability (agent count)** | Practical limit ~5-10 teammates | 20+ agents demonstrated | tmux is **better** for large-scale parallelism |
| **Cross-repo coordination** | Single project only | Any pane can target any directory | tmux is **better** for multi-project workflows |
| **Cost control** | No built-in budgets per teammate | Can use different models/settings per session | tmux offers **more granular** cost control |
| **Quality gates** | Native hooks (TeammateIdle, TaskCompleted) | Must implement custom checks | Teams has hooks; tmux needs wrapper scripts |
| **Plan approval** | Built-in plan mode with lead approval | No equivalent without custom tooling | Teams has this natively; tmux has no built-in equivalent |
| **File conflict prevention** | Guidance-based ("avoid same-file edits") | Lock files, git worktrees | tmux is **better** with git worktrees for hard isolation |
| **Observability** | Shift+Down or split panes | `tmux capture-pane`, monitoring dashboards | tmux is **better** for real-time monitoring of many agents |
| **Error recovery** | Teammates may stop on errors | Sessions are independent; manual restart | tmux is **better**; frameworks like agent_farm have auto-restart |
| **Non-Claude integration** | Claude Code only | Any process can occupy a tmux pane | tmux is **better** for heterogeneous tool orchestration |
| **Setup complexity** | One env var to enable | Significant scripting required | Teams is **much simpler** to get started |
| **Stability** | Experimental with known bugs | Battle-tested (tmux is decades old) | tmux infrastructure is **more stable**; coordination still manual |

---

## Decision Matrix

Use this matrix to pick the right approach based on your situation:

| Scenario | Recommended | Rationale |
|:---------|:----------:|:----------|
| Quick parallel research/review | **Agent Teams** | Low setup cost, built-in coordination, natural language tasking |
| Parallel feature development (same repo) | **Agent Teams** | Shared task list and messaging reduce coordination overhead |
| Large-scale automated codebase sweeps | **DIY tmux** | Better scalability (20+ agents), auto-restart, custom workflows |
| Multi-repository coordination | **DIY tmux** | Agent Teams is limited to a single project |
| Long-running unattended work | **DIY tmux** | tmux session persistence; no session resumption issues |
| Debugging with competing hypotheses | **Agent Teams** | Native adversarial debate pattern with direct messaging |
| Mixed tooling (Claude + other tools) | **DIY tmux** | Any process can be a pane; not limited to Claude Code |
| Quick setup, minimal scripting | **Agent Teams** | One environment variable vs. custom orchestration scripts |
| Production/CI pipeline integration | **DIY tmux** | More predictable, scriptable, and no experimental feature dependency |
| Cost-sensitive parallel work | **DIY tmux** | More control over model selection and token budgets per agent |

---

## Hybrid Approach

The two approaches are not mutually exclusive. A practical hybrid pattern:

1. **Use Agent Teams** for interactive, conversational coordination where
   teammates need to discuss findings, challenge each other, and converge
   on decisions.
2. **Use DIY tmux** for batch operations, long-running sweeps, and
   CI/CD-integrated workflows where persistence and scalability matter.
3. **Agent Teams already uses tmux** under the hood for split-pane display
   mode, so the infrastructure overlaps.

---

## Key Takeaways

- **Agent Teams** is the right choice when you want structured coordination
  with minimal setup and your work fits within a single project. Its native
  messaging, task management, and dependency resolution make it significantly
  easier to get parallel agents collaborating. The main drawbacks are its
  experimental status, session resumption bugs, and higher token cost.

- **DIY tmux** is the right choice when you need maximum control,
  scalability beyond ~10 agents, cross-project coordination, or long-running
  unattended workflows. The trade-off is that you must build and maintain
  the coordination layer yourself (or adopt a community framework).

- **Agent Teams is evolving quickly.** As an experimental feature, many of
  its current limitations (session resumption, single team per session, no
  nested teams) are likely to be addressed in future releases. The DIY tmux
  approach may become less necessary as Agent Teams matures.

---

## Sources

- [Orchestrate teams of Claude Code sessions - Official Docs](https://code.claude.com/docs/en/agent-teams)
- [Claude Code Agent Teams: The Complete Guide 2026](https://claudefa.st/blog/guide/agents/agent-teams)
- [Claude Code Agent Teams: Run Parallel AI Agents - SitePoint](https://www.sitepoint.com/anthropic-claude-code-agent-teams/)
- [How to Set Up and Use Claude Code Agent Teams - Medium](https://darasoba.medium.com/how-to-set-up-and-use-claude-code-agent-teams-and-actually-get-great-results-9a34f8648f6d)
- [Multi-agent Claude Code workflow using tmux - GitHub Gist](https://gist.github.com/andynu/13e362f7a5e69a9f083e7bca9f83f60a)
- [claude_code_agent_farm - GitHub](https://github.com/Dicklesworthstone/claude_code_agent_farm)
- [Claude Code + tmux: The Ultimate Terminal Workflow](https://www.blle.co/blog/claude-code-tmux-beautiful-terminal)
- [From Tasks to Swarms: Agent Teams in Claude Code](https://alexop.dev/posts/from-tasks-to-swarms-agent-teams-in-claude-code/)
- [Claude Code's Hidden Multi-Agent System](https://paddo.dev/blog/claude-code-hidden-swarm/)
