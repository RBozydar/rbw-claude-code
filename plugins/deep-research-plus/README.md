# Deep Research Plus

Advanced research plugin combining **deep web research** with **GDELT-powered geopolitical analysis**. Uses a unified skill with domain-based routing for specialized research.

## What This Plugin Does

Transforms Claude Code into a deep research agent by orchestrating:
- **Domain Detection** - Auto-routes queries to specialized research domains
- **Parallel Research Workers** - Independent agents that investigate specific topics
- **Gap Detection** - Objective evaluation of coverage completeness
- **Iterative Refinement** - Multiple rounds until comprehensive coverage
- **Structured Synthesis** - Coherent reports with full citations

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              MAIN CLAUDE (Orchestrator)                  │
│  - Detects domain (general | geopolitical)              │
│  - Loads domain config (agents, tools, gap dimensions)  │
│  - Spawns domain-specific workers in parallel           │
│  - Synthesizes findings                                 │
│  - Produces final report with domain-appropriate format │
└──────────────────────────┬──────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │       DOMAIN ROUTING          │
           ├───────────────────────────────┤
           │ general → core:* agents       │
           │ geopolitical → geo:* agents   │
           └───────────────┬───────────────┘
                           │
   ┌───────────┬───────────┼───────────┬──────────────┐
   ▼           ▼           ▼           ▼              ▼
┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐     ┌───────────┐
│Worker│   │Worker│   │Worker│   │Worker│     │    Gap    │
│  1   │   │  2   │   │  3   │   │  N   │     │ Detector  │
└──────┘   └──────┘   └──────┘   └──────┘     └───────────┘
   │           │           │           │              │
   └───────────┴───────────┴───────────┴──────────────┘
                           │
                    ┌──────▼──────┐
                    │  Synthesis  │
                    │   + Draft   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │Final Report │
                    │ + Citations │
                    └─────────────┘
```

## Installation

```bash
# In your target project directory
claude plugin add /path/to/rbw-claude-code/plugins/deep-research-plus
```

### Enable GDELT MCP Server (for geopolitical research)

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "gdelt": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "/path/to/rbw-claude-code/plugins/deep-research-plus/mcp-server"
    }
  }
}
```

Install dependencies once:

```bash
cd /path/to/rbw-claude-code/plugins/deep-research-plus/mcp-server && uv sync
```

## Usage

### Invoke the Skill

```
/deep-research <query>
```

Or naturally in conversation:
- "Do deep research on quantum computing in healthcare"
- "Research the current state of the Russia-Ukraine conflict"

### Domain Auto-Detection

The skill automatically detects which domain to use:

| Query Contains | Domain Used |
|---------------|-------------|
| conflict, war, military, sanctions, embargo, bilateral, GDELT | **geopolitical** |
| Anything else | **general** |

### Explicit Domain Selection

Override auto-detection with a flag:

```
/deep-research --domain=geopolitical "semiconductor supply chain analysis"
```

## Domains

### General (Default)

- **Prefix**: `core`
- **Agents**: `deep-research:core:research-worker`, `deep-research:core:gap-detector`
- **Tools**: WebSearch, WebFetch
- **Use for**: Technology, business, science, general topics

### Geopolitical

- **Prefix**: `geo`
- **Agents**: Specialized analysts (conflict, sanctions, actors, sentiment, trends)
- **Tools**: GDELT MCP tools + WebSearch
- **Use for**: Conflicts, sanctions, international relations, media analysis

## Agents

### Core Agents (General Domain)

| Agent | Purpose |
|-------|---------|
| `deep-research:core:research-worker` | Autonomous investigator for a single topic |
| `deep-research:core:gap-detector` | Objective evaluator of research coverage |
| `deep-research:core:research-orchestrator` | Autonomous orchestrator for background mode |

### Geopolitical Agents

| Agent | Purpose |
|-------|---------|
| `deep-research:geo:conflict-analyst` | Armed conflicts, escalation patterns (CAMEO codes 14-20) |
| `deep-research:geo:sanctions-researcher` | Sanctions regimes, OFAC/EU designations |
| `deep-research:geo:actor-mapper` | Actor relationship networks |
| `deep-research:geo:sentiment-tracker` | Media tone and narrative analysis |
| `deep-research:geo:trend-analyst` | Coverage trend patterns |
| `deep-research:geo:gap-detector-geo` | Geopolitical coverage evaluation |

## Workflows

### General Workflows

| Workflow | When to Use |
|----------|-------------|
| `quick-research` | Simple queries, single-dimension topics |
| `targeted-research` | User-specified dimensions to compare |
| `background-research` | Fire-and-forget autonomous research |

### Geopolitical Workflows

| Workflow | When to Use |
|----------|-------------|
| `geopolitical/conflict-analysis` | Deep conflict analysis pattern |
| `geopolitical/sanctions-research` | Sanctions regime investigation |
| `geopolitical/narrative-analysis` | Media sentiment tracking |

## MCP Server Tools (GDELT)

| Tool | Description |
|------|-------------|
| `gdelt_events` | Query CAMEO-coded events |
| `gdelt_gkg` | Global Knowledge Graph - entities, themes, tone |
| `gdelt_actors` | Map actor relationships for a country |
| `gdelt_trends` | Coverage volume/tone over time |
| `gdelt_doc` | Full-text article search |
| `gdelt_cameo_lookup` | CAMEO code meanings and Goldstein scale |

## Directory Structure

```
deep-research-plus/
├── skills/
│   └── deep-research/
│       ├── SKILL.md              # Unified skill with domain routing
│       ├── domains/
│       │   ├── general.md        # General domain config
│       │   └── geopolitical.md   # Geopolitical domain config
│       └── workflows/
│           ├── quick-research.md
│           ├── targeted-research.md
│           ├── background-research.md
│           └── geopolitical/
│               ├── conflict-analysis.md
│               ├── sanctions-research.md
│               └── narrative-analysis.md
├── agents/
│   ├── core/                     # General research agents
│   │   ├── research-worker.md
│   │   ├── gap-detector.md
│   │   └── research-orchestrator.md
│   └── geopolitical/             # Geopolitical specialist agents
│       ├── conflict-analyst.md
│       ├── sanctions-researcher.md
│       ├── actor-mapper.md
│       ├── sentiment-tracker.md
│       ├── trend-analyst.md
│       └── gap-detector-geo.md
└── mcp-server/                   # GDELT MCP server
    └── server.py
```

## Research Methodology

The skill uses a **diffusion-based research loop**:

1. **Domain Detection** - Classify query and load appropriate domain config
2. **Query Refinement** - Clarify scope and objectives with user
3. **Parallel Workers** - Dispatch domain-specific specialists with topic isolation
4. **Gap Detection** - Evaluate coverage using domain-specific dimensions (70% threshold)
5. **Iterative Refinement** - Fill gaps with targeted follow-up
6. **Synthesis** - Generate structured report with domain-appropriate format

## Execution Modes

### Interactive Mode (Default)

Main Claude orchestrates the research with user collaboration:

1. **Domain Detection** - Auto-detect or user override
2. **Refinement Phase** - Validate domain, dimensions, depth with user
3. **Diffusion Loop** - Workers research, Claude synthesizes, gap detector evaluates
4. **Mid-Research Steering** - User can redirect focus, switch domains, or stop early
5. **Final Report** - Polished output with domain-specific sections

### Background Mode

For "fire and forget" research when user has other work:

```
Task(
  subagent_type: "deep-research:core:research-orchestrator",
  prompt: "Research: [topic]",
  run_in_background: true
)
```

## Adding New Domains

To add a new research domain (e.g., finance):

1. Create `domains/finance.md` with:
   - Trigger keywords
   - Worker agents
   - Gap detector configuration
   - Output template

2. Create agents in `agents/finance/`:
   - Specialist workers
   - Domain-specific gap detector

3. Update SKILL.md domain detection logic

4. (Optional) Add workflows in `workflows/finance/`

## Output

Reports are saved to `research_output/[topic]_[date].md` with:

1. Metadata header (domain, iterations, workers)
2. Executive summary
3. Key findings with citations
4. Domain-specific sections
5. Methodology note
6. Complete source list

## Requirements

- Claude Code with Task tool support
- WebSearch and WebFetch tools available
- GDELT MCP server (for geopolitical domain)
- No external dependencies for general domain

## License

MIT
