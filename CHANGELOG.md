# Changelog

All notable changes to rbw-claude-code will be documented in this file.

## [1.5.0] - 2025-01-24

### Added

#### Core Plugin
- **learnings-researcher agent** - Surfaces institutional knowledge from `docs/solutions/` during planning
- **brainstorming skill** - Structured ideation and brainstorming workflows
- **agent-native-audit command** - Audit code for agent accessibility
- **deepen-plan command** - Enhance plans with parallel research agents for each section
- **import-tasks skill** - Import tasks from planning sessions into work sessions

#### workflows:plan Enhancements
- **Step 0: Idea Refinement** - Checks for brainstorm documents, runs gemini-brainstorm for alternative perspectives
- **Step 1: Local Research** - Always runs repo-research-analyst and learnings-researcher in parallel
- **Step 1.5: Research Decision** - Explicit user confirmation before external research (skip/research/specific topic)
- **Step 1.5b: External Research** - Conditional best-practices and framework-docs research
- **Step 1.6: Consolidate Research** - Merges findings before planning
- Added `/deepen-plan` to post-generation options

#### workflows:work Enhancements
- **Incremental commits table** - Decision guide for when to create incremental commits
- **Plan checkbox tracking** - Mark off `[ ]` → `[x]` as tasks complete
- **Task import from plans** - Import tasks via `task_list_id` in plan frontmatter
- **Parallel subagent execution** - Spawn coordinated subagents for large plans

### Changed
- Updated year references to 2026
- Core plugin: 14 → 22 agents, 13 → 17 commands, 7 → 13 skills
- Python-backend plugin: 5 → 7 agents, added 1 skill

## [1.4.1] - Previous Release

Initial tracked version with core, python-backend, and utility plugins.
