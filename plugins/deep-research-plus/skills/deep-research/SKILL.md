---
name: deep-research
description: This skill should be used when thorough, multi-perspective research with citations is needed. It performs comprehensive research using a diffusion research loop with domain specialization, supporting general web research and specialized domains (geopolitical with GDELT). Auto-detects domain from query or accepts an explicit --domain flag.
---

<objective>

Execute deep, comprehensive research using a multi-agent diffusion loop with domain-aware specialization:
1. Classify query and detect appropriate domain
2. Break down the query into research dimensions using domain config
3. Spawn parallel worker agents appropriate for the domain
4. Synthesize findings into a coherent draft
5. Use domain-specific gap detection to identify missing coverage
6. Iterate until coverage is sufficient
7. Produce a final report with citations in domain-appropriate format

</objective>

<essential_principles>

## The Diffusion Research Pattern

This skill implements **Self-Balancing Test-Time Diffusion** -- starting with a noisy/speculative understanding and iteratively refining through parallel, isolated research workers.

1. **Domain Awareness**: Different research domains require different tools, agents, and evaluation criteria. Auto-detect domain or accept explicit specification.
2. **Worker Isolation**: Each worker receives ONLY their assigned topic. They cannot see other workers' findings, the current draft, or the full brief. This prevents herd behavior.
3. **Gap Detection Objectivity**: Use a separate gap-detector agent (not the orchestrator) to evaluate coverage. This avoids self-evaluation bias.
4. **Conservative Iteration**: Continue if coverage < 70% of core questions or any critical question is unanswered. Stop at diminishing returns.
5. **Quality Over Quantity**: 3-5 well-sourced findings per worker beats 10 weakly-sourced ones.

</essential_principles>

<domains>

## Available Domains

### General (Default)
- **Config**: [references/domains/general.md](./references/domains/general.md)
- **Agents**: `deep-research:core:research-worker`, `deep-research:core:gap-detector`
- **Tools**: WebSearch, WebFetch

### Geopolitical
- **Triggers**: conflict, war, sanctions, bilateral relations, media coverage, GDELT, CAMEO
- **Config**: [references/domains/geopolitical.md](./references/domains/geopolitical.md)
- **Agents**: Specialized analysts (conflict, sanctions, actors, sentiment, trends)
- **Tools**: GDELT MCP tools + WebSearch

### Domain Detection

```
IF query contains (conflict, war, military, sanctions, embargo, bilateral,
   alliance, media coverage, sentiment, GDELT, CAMEO):
   → GEOPOLITICAL domain
ELSE:
   → GENERAL domain
```

Override: `/deep-research --domain=geopolitical "query"`

</domains>

<available_workflows>

## Workflow Variants

Load the appropriate workflow for the research mode:

| Workflow | When to Use |
|----------|-------------|
| [references/workflows/quick-research.md](./references/workflows/quick-research.md) | Quick overview, 1 iteration |
| [references/workflows/targeted-research.md](./references/workflows/targeted-research.md) | Focused research on specific dimensions |
| [references/workflows/background-research.md](./references/workflows/background-research.md) | Autonomous background research |
| [references/workflows/geopolitical/conflict-analysis.md](./references/workflows/geopolitical/conflict-analysis.md) | Conflict-specific geopolitical analysis |
| [references/workflows/geopolitical/sanctions-research.md](./references/workflows/geopolitical/sanctions-research.md) | Sanctions-focused research |
| [references/workflows/geopolitical/narrative-analysis.md](./references/workflows/geopolitical/narrative-analysis.md) | Media narrative analysis |

</available_workflows>

<algorithm>

## The Research Loop

```
PHASE 0: DOMAIN CLASSIFICATION & REFINEMENT
├── Parse query and detect domain
├── Load domain config from references/domains/
├── Generate draft research brief
├── Present brief to user via AskUserQuestion (domain, dimensions, depth)
├── Refine based on feedback
└── Proceed when confirmed

PHASE 1: INITIALIZATION
├── Finalize research brief
├── Select domain-appropriate agents
└── Generate initial speculative draft

PHASE 2: DIFFUSION LOOP (max 3 iterations)
├── SPAWN WORKERS: 2-5 domain-specific workers in PARALLEL (single message)
├── SYNTHESIZE: Merge findings, resolve contradictions, add citations
├── GAP DETECTION: Launch domain-specific gap-detector
└── Decision: CONTINUE (spawn more workers for gaps) or COMPLETE

PHASE 3: FINAL REPORT
├── Polish using domain output template from config
├── Compile all sources with descriptions
└── Add executive summary
```

**Interactive (default):** Orchestrate directly, can ask questions mid-research.
**Background:** Spawn `deep-research:core:research-orchestrator` for autonomous operation.

</algorithm>

<execution_guide>

## Phase 0: Domain Classification

Analyze the query for domain signals. Present a draft research brief with detected domain, proposed dimensions, key questions, and specialist agents (if geopolitical). Validate with user via AskUserQuestion for domain, dimensions, and depth level.

## Phase 1: Spawn Workers

Load worker prompt templates from the appropriate domain config file:
- **General**: See [references/domains/general.md](./references/domains/general.md) for worker prompt template
- **Geopolitical**: See [references/domains/geopolitical.md](./references/domains/geopolitical.md) for specialist agent prompts

**Critical**: Spawn ALL workers in a SINGLE message with multiple Task tool calls for true parallel execution.

## Phase 2: Synthesis and Gap Detection

After workers return, merge findings into a structured draft with citations. Then launch the domain-specific gap-detector:
- **General**: `deep-research:core:gap-detector`
- **Geopolitical**: `deep-research:geo:gap-detector-geo` (uses weighted coverage dimensions from domain config)

If gaps found, spawn targeted workers for those specific gaps. Maximum 3 iterations.

## Phase 3: Final Report

Use domain-specific output template from the domain config file. Save to `research_output/[topic-slug]_[date].md` (or `research_output/geo/` for geopolitical).

Required sections: Metadata header, Executive summary, Key findings with sources, Detailed analysis, Methodology note, Complete source list. Additional domain-specific sections are defined in each domain config.

</execution_guide>

<mid_research_steering>

## Mid-Research Steering

| User Says | Action |
|-----------|--------|
| "Focus more on X" | Add X-related topics to next worker batch |
| "Skip Y" | Remove Y from remaining work |
| "Go deeper on Z" | Spawn additional worker for Z |
| "That's enough" | Skip remaining iterations, produce final report |
| "Switch to geopolitical" | Reload domain config, adjust agents |

</mid_research_steering>

<success_criteria>

Research is complete when:
- All core questions from the brief are addressed
- Coverage score >= 70% (from gap detector)
- Key findings are well-sourced (2+ citations each)
- Contradictions are noted and explained
- Maximum 3 iterations reached

Research is NOT complete just because the draft reads well or workers stopped returning new information. Always use the domain-appropriate gap-detector for objective evaluation.

</success_criteria>
