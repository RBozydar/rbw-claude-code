# Deep Research Plus

Advanced research plugin combining **deep web research** with **GDELT-powered geopolitical analysis**. Standalone plugin with its own marketplace - install only where needed.

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

## Skills

| Skill | Description |
|-------|-------------|
| `/deep-research <query>` | General deep research with parallel workers and gap detection |
| `/geo-research <query>` | GDELT-powered geopolitical research |

## Agents

### General Research
| Agent | Purpose |
|-------|---------|
| `research-worker` | Isolated web research on specific topics |
| `gap-detector` | Evaluate coverage completeness |
| `research-orchestrator` | Background autonomous research |

### Geopolitical Specialists
| Agent | Purpose |
|-------|---------|
| `conflict-analyst` | Armed conflicts, escalation patterns (CAMEO codes 14-20) |
| `sanctions-researcher` | Sanctions regimes, OFAC/EU designations |
| `actor-mapper` | Actor relationship networks |
| `sentiment-tracker` | Media tone and narrative analysis |
| `trend-analyst` | Coverage trend patterns |
| `gap-detector-geo` | Geopolitical coverage evaluation |

## MCP Server Tools (GDELT)

| Tool | Description |
|------|-------------|
| `gdelt_events` | Query CAMEO-coded events |
| `gdelt_gkg` | Global Knowledge Graph - entities, themes, tone |
| `gdelt_actors` | Map actor relationships for a country |
| `gdelt_trends` | Coverage volume/tone over time |
| `gdelt_doc` | Full-text article search |
| `gdelt_cameo_lookup` | CAMEO code meanings and Goldstein scale |

## Architecture

```
deep-research-plus/
├── agents/
│   ├── research-worker.md       # General research
│   ├── gap-detector.md          # General gap detection
│   ├── research-orchestrator.md # Background orchestrator
│   ├── conflict-analyst.md      # Geopolitical
│   ├── sanctions-researcher.md
│   ├── actor-mapper.md
│   ├── sentiment-tracker.md
│   ├── trend-analyst.md
│   └── gap-detector-geo.md
├── skills/
│   ├── deep-research/           # /deep-research skill
│   │   └── workflows/
│   └── geo-research/            # /geo-research skill
│       └── workflows/
└── mcp-server/                  # GDELT MCP server
    └── server.py
```

## Research Methodology

Both skills use a **diffusion-based research loop**:

1. **Query Refinement** - Clarify scope and objectives
2. **Parallel Workers** - Dispatch specialists with topic isolation
3. **Gap Detection** - Evaluate coverage (70% threshold)
4. **Iterative Refinement** - Fill gaps with targeted follow-up
5. **Synthesis** - Generate structured report with citations

## License

MIT
