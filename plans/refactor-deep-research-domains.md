# Plan: Domain-Based Deep Research System

## Overview

Refactor `deep-research-plus` to eliminate algorithm duplication between `deep-research` and `geo-research` skills by creating a unified skill with domain routing.

## Design Decisions (User Confirmed)

- **Agent naming**: `deep-research:geo:conflict-analyst` (hierarchical with colons)
- **Skill entry point**: Unified `/deep-research` only (auto-detection + `--domain` flag)
- **Workflows**: Keep geo workflows, organize in `workflows/geopolitical/` subdirectory

## Current Problems

1. **Algorithm Duplication**: ~70% of `geo-research/SKILL.md` duplicates `deep-research/SKILL.md`
2. **Naming Inconsistency**: SKILL.md uses `geopolitical-research:` but workflows use `geo-research:`
3. **Maintenance Burden**: Changes to the diffusion loop must be made in two places
4. **Not Extensible**: Adding a new domain (finance, security) requires copying the entire algorithm

## Target Architecture

```
deep-research-plus/
├── skills/
│   └── deep-research/
│       ├── SKILL.md              # Unified skill with domain routing
│       ├── domains/
│       │   ├── general.md        # Default domain config
│       │   └── geopolitical.md   # GDELT-powered geo research
│       └── workflows/
│           ├── quick-research.md
│           ├── targeted-research.md
│           ├── background-research.md
│           └── geopolitical/     # Domain-specific workflows
│               ├── conflict-analysis.md
│               ├── sanctions-research.md
│               └── narrative-analysis.md
├── agents/
│   ├── core/                     # Shared agents
│   │   ├── research-worker.md
│   │   ├── gap-detector.md
│   │   └── research-orchestrator.md
│   └── geopolitical/             # Domain-specific agents
│       ├── conflict-analyst.md
│       ├── sanctions-researcher.md
│       ├── actor-mapper.md
│       ├── sentiment-tracker.md
│       ├── trend-analyst.md
│       └── gap-detector-geo.md
└── mcp-server/                   # Unchanged
```

## Implementation Steps

### Step 1: Reorganize Agents Directory

Move agents into subdirectories:

```bash
agents/core/
  research-worker.md      # from agents/research-worker.md
  gap-detector.md         # from agents/gap-detector.md
  research-orchestrator.md # from agents/research-orchestrator.md

agents/geopolitical/
  conflict-analyst.md     # from agents/conflict-analyst.md
  sanctions-researcher.md # from agents/sanctions-researcher.md
  actor-mapper.md         # from agents/actor-mapper.md
  sentiment-tracker.md    # from agents/sentiment-tracker.md
  trend-analyst.md        # from agents/trend-analyst.md
  gap-detector-geo.md     # from agents/gap-detector-geo.md
```

### Step 2: Create Domain Config Files

**`skills/deep-research/domains/general.md`**:
- Default domain for non-specialized queries
- Uses `core/research-worker` agents
- Uses `core/gap-detector` for coverage evaluation
- Output format from current deep-research skill

**`skills/deep-research/domains/geopolitical.md`**:
- Triggers: conflict, sanctions, actors, narrative keywords
- Query routing table (conflict→conflict-analyst, etc.)
- GDELT MCP tools list
- Geo-specific gap detection dimensions
- Geo-specific output sections (GDELT metrics, Goldstein analysis)

### Step 3: Create Unified SKILL.md

New structure:
```
---
name: deep-research
description: Comprehensive research using diffusion loop with domain specialization
---

<objective>...</objective>

<domain_classification>
  - Query analysis
  - Domain detection (general | geopolitical | ...)
  - Load domain config
</domain_classification>

<algorithm>
  Phase 0: Query Refinement (with domain-specific options)
  Phase 1: Initialization (uses domain.agents)
  Phase 2: Diffusion Loop (uses domain.gap_detector)
  Phase 3: Final Report (uses domain.output_template)
</algorithm>

<execution_guide>
  - Domain-aware worker spawning
  - Domain-aware gap detection
  - Domain-aware output formatting
</execution_guide>

<domains>
  Reference to domains/*.md files
</domains>
```

### Step 4: Remove geo-research Skill

Delete `skills/geo-research/` directory entirely. Its functionality is absorbed into the unified skill with `geopolitical` domain.

### Step 5: Update Agent References

Standardize naming convention with hierarchical format:
- Core agents: `deep-research:core:research-worker`, `deep-research:core:gap-detector`
- Geopolitical agents: `deep-research:geo:conflict-analyst`, `deep-research:geo:sanctions-researcher`, etc.

Pattern: `deep-research:<domain>:<agent-name>`

### Step 6: Update README.md

- Remove `/geo-research` skill documentation
- Add domain system explanation
- Update agent table with new paths
- Add domain extension guide

## Files to Modify

| File | Action |
|------|--------|
| `skills/deep-research/SKILL.md` | Rewrite with domain routing |
| `skills/deep-research/domains/general.md` | Create |
| `skills/deep-research/domains/geopolitical.md` | Create |
| `skills/deep-research/workflows/geopolitical/` | Create directory |
| `skills/geo-research/workflows/*.md` | Move to `skills/deep-research/workflows/geopolitical/` |
| `skills/geo-research/` | Delete directory (after moving workflows) |
| `agents/research-worker.md` | Move to `agents/core/` |
| `agents/gap-detector.md` | Move to `agents/core/` |
| `agents/research-orchestrator.md` | Move to `agents/core/` |
| `agents/conflict-analyst.md` | Move to `agents/geopolitical/` |
| `agents/sanctions-researcher.md` | Move to `agents/geopolitical/` |
| `agents/actor-mapper.md` | Move to `agents/geopolitical/` |
| `agents/sentiment-tracker.md` | Move to `agents/geopolitical/` |
| `agents/trend-analyst.md` | Move to `agents/geopolitical/` |
| `agents/gap-detector-geo.md` | Move to `agents/geopolitical/` |
| `README.md` | Update documentation |

## Domain Config Format

Each domain file follows this structure:

```markdown
---
name: geopolitical
prefix: geo
triggers:
  - conflict, war, military, violence, escalation
  - sanctions, embargo, OFAC, trade restrictions
  - bilateral relations, alliances, networks
  - media coverage, sentiment, narrative
---

## Worker Agents
| Query Type | Primary Agent | Supporting |
|------------|---------------|------------|
| conflict | deep-research:geo:conflict-analyst | deep-research:geo:actor-mapper |
| sanctions | deep-research:geo:sanctions-researcher | deep-research:geo:trend-analyst |
| actors | deep-research:geo:actor-mapper | deep-research:geo:trend-analyst |
| narrative | deep-research:geo:sentiment-tracker | deep-research:geo:trend-analyst |

## Gap Detector
agent: deep-research:geo:gap-detector-geo
dimensions:
  core (3x): Temporal, Actor, DataSource
  supporting (2x): Quantification, Geographic, Perspective
  contextual (1x): Precedents, Expert, Timeline

## Tools
- gdelt_events, gdelt_gkg, gdelt_actors
- gdelt_trends, gdelt_doc, gdelt_cameo_lookup
- WebSearch (supplemental)

## Output Sections
- GDELT Quantitative Metrics
- Actor Relationship Matrix
- Goldstein Scale Analysis
- CAMEO Event Distribution

## Query Routing Logic
[Decision tree for conflict vs sanctions vs actors vs narrative]
```

**General domain** (`domains/general.md`):
```markdown
---
name: general
prefix: core
triggers: [] # default fallback
---

## Worker Agents
| Query Type | Agent |
|------------|-------|
| any | deep-research:core:research-worker |

## Gap Detector
agent: deep-research:core:gap-detector
dimensions:
  core (3x): [Core questions addressed]
  supporting (2x): [Supporting context]
  contextual (1x): [Nice to have]

## Tools
- WebSearch
- WebFetch

## Output Sections
- Executive Summary
- Key Findings
- Detailed Analysis
- Limitations
- Sources
```

## Verification

1. **Skill invocation**: Run `/deep-research "quantum computing applications"` - should use general domain
2. **Domain detection**: Run `/deep-research "Russia-Ukraine conflict analysis"` - should detect geopolitical domain
3. **Agent spawning**: Verify correct agents are spawned based on domain
4. **Gap detection**: Verify domain-appropriate gap detector is used
5. **Output format**: Verify domain-specific sections appear in final report

## Execution Order

1. Create `agents/core/` and `agents/geopolitical/` directories
2. Move core agents to `agents/core/`
3. Move geopolitical agents to `agents/geopolitical/`
4. Create `skills/deep-research/domains/` directory
5. Create `domains/general.md`
6. Create `domains/geopolitical.md` (extract from geo-research/SKILL.md)
7. Create `skills/deep-research/workflows/geopolitical/` directory
8. Move geo workflows to the new directory
9. Rewrite `skills/deep-research/SKILL.md` with domain routing
10. Delete `skills/geo-research/` directory
11. Update `README.md`
12. Test with sample queries

## Rollback Plan

If issues arise, the original files can be restored from git since we're making atomic commits.
