# Geopolitical Research Agent

A specialized Claude Code plugin for geopolitical research using GDELT (Global Database of Events, Language, and Tone) data. Provides structured analysis of international events, conflicts, sanctions, actor relationships, and media narratives.

## Features

- **Conflict Analysis**: Track armed conflicts, escalation patterns, and actor relationships using CAMEO-coded events
- **Sanctions Research**: Monitor sanctions regimes, enforcement actions, economic impacts, and evasion patterns
- **Actor Mapping**: Analyze relationships between countries, organizations, and key figures
- **Narrative Analysis**: Track media sentiment and coverage patterns across regions

## Architecture

```
geopolitical-research/
├── .claude-plugin/
│   └── plugin.json           # Plugin configuration
├── mcp-server/               # GDELT MCP Server
│   ├── server.py            # FastMCP server with GDELT tools
│   ├── pyproject.toml       # Dependencies
│   └── README.md            # Server documentation
├── agents/                   # Specialized research agents
│   ├── conflict-analyst.md  # Armed conflict specialist
│   ├── sanctions-researcher.md  # Sanctions specialist
│   ├── actor-mapper.md      # Relationship analysis
│   ├── sentiment-tracker.md # Media sentiment analysis
│   ├── trend-analyst.md     # Coverage trend analysis
│   └── gap-detector-geo.md  # Geopolitical coverage evaluator
└── skills/
    └── geo-research/
        ├── SKILL.md         # Main skill router
        └── workflows/
            ├── conflict-analysis.md
            ├── sanctions-research.md
            └── narrative-analysis.md
```

## MCP Server Tools

The GDELT MCP server exposes these tools:

| Tool | Description |
|------|-------------|
| `gdelt_events` | Query CAMEO-coded events with actor/type filtering |
| `gdelt_gkg` | Global Knowledge Graph - entities, themes, tone |
| `gdelt_actors` | Map actor relationships for a country |
| `gdelt_trends` | Coverage volume/tone trends over time |
| `gdelt_doc` | Full-text article search |
| `gdelt_cameo_lookup` | CAMEO code meanings and Goldstein scale |

## Usage

Invoke the skill with:
```
/geo-research <query>
/geo <query>
```

### Examples

```
/geo-research Analyze the Russia-Ukraine conflict escalation in the past 30 days
/geo What sanctions have been imposed on Iran and their economic impact?
/geo Map the key actors in the South China Sea disputes
/geo How has media coverage of the Israel-Palestine conflict changed?
```

## Prerequisites

- Python 3.11+
- [py-gdelt](https://github.com/RBozydar/py-gdelt) library
- MCP-compatible Claude Code installation

## Setup

1. Install dependencies in the MCP server:
   ```bash
   cd mcp-server
   uv sync
   ```

2. The MCP server will be automatically started when the plugin loads (configured in `plugin.json`)

## Data Sources

This plugin leverages GDELT's data infrastructure:

- **Events Database**: 300+ million events since 1979, updated every 15 minutes
- **Global Knowledge Graph (GKG)**: Extracted entities, themes, and sentiment from news
- **DOC API**: Full-text search across monitored news sources (3-month window)
- **CAMEO Codes**: Standardized event classification with Goldstein conflict/cooperation scale

## Research Methodology

The plugin implements a diffusion-based research loop:

1. **Query Refinement**: Clarify research scope and objectives
2. **Specialist Dispatch**: Route to appropriate specialist agents in parallel
3. **Gap Detection**: Evaluate coverage completeness using weighted dimensions
4. **Iterative Refinement**: Fill gaps with targeted follow-up research
5. **Synthesis**: Generate structured report with citations

## License

MIT
