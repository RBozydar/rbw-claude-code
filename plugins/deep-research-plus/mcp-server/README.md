# GDELT MCP Server Configuration

This folder contains configuration for the GDELT MCP server, which is now part of the [py-gdelt](https://github.com/RBozydar/py-gdelt) library.

## Setup

The MCP server is included in py-gdelt and can be run directly without any local installation.

### Claude Desktop / Claude Code

Copy the configuration from `claude_desktop_config.json` to your Claude settings:

```json
{
  "mcpServers": {
    "gdelt-research": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "gdelt-py[mcp]",
        "python",
        "-m",
        "py_gdelt.mcp_server.server"
      ]
    }
  }
}
```

This will automatically install py-gdelt with MCP support and run the server.

### Alternative: Local Installation

If you prefer to install py-gdelt locally:

```bash
pip install gdelt-py[mcp]
# or with uv
uv pip install gdelt-py[mcp]
```

Then use this config:

```json
{
  "mcpServers": {
    "gdelt-research": {
      "command": "python",
      "args": ["-m", "py_gdelt.mcp_server.server"]
    }
  }
}
```

## Available Tools

The MCP server provides 6 tools for geopolitical research:

| Tool | Description |
|------|-------------|
| `gdelt_events` | Query CAMEO-coded events with aggregated statistics |
| `gdelt_gkg` | Query Global Knowledge Graph for entities and themes |
| `gdelt_actors` | Map actor relationships between countries |
| `gdelt_trends` | Get coverage trends over time |
| `gdelt_doc` | Full-text article search |
| `gdelt_cameo_lookup` | Look up CAMEO code meanings |

## Documentation

For full documentation, see:
- [py-gdelt MCP Server README](https://github.com/RBozydar/py-gdelt/tree/main/src/py_gdelt/mcp_server)
- [py-gdelt Documentation](https://rbozydar.github.io/py-gdelt/)

## Performance

All tools use **streaming aggregation** with O(1) memory consumption, allowing queries spanning weeks or months without OOM issues.
