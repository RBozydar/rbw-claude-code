# GDELT MCP Server

MCP server exposing the py-gdelt library for geopolitical research agents.

## Overview

This MCP server provides structured access to GDELT (Global Database of Events, Language, and Tone) data sources through 6 specialized tools. It's designed for AI agents conducting geopolitical analysis, conflict monitoring, and news research.

## Installation

```bash
cd /home/rbw/repo/rbw-claude-code/plugins/geopolitical-research/mcp-server
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Running the Server

```bash
python server.py
```

## Available Tools

### 1. `gdelt_events`
Query CAMEO-coded events from GDELT Events database.

**Parameters:**
- `actor1_country` (str, optional): ISO3 country code for actor 1 (e.g., "USA", "RUS", "CHN")
- `actor2_country` (str, optional): ISO3 country code for actor 2
- `event_type` (str, default="all"): Filter by event type - "conflict", "cooperation", or "all"
- `days_back` (int, default=7): Number of days to look back (max: 365)
- `min_goldstein` (float, optional): Minimum Goldstein scale (-10 to 10, negative=conflict)
- `max_goldstein` (float, optional): Maximum Goldstein scale (-10 to 10, positive=cooperation)

**Returns:** List of event summaries with global_event_id, actors, event codes, Goldstein scale, tone, and source URLs.

**Example:**
```json
{
  "actor1_country": "USA",
  "actor2_country": "CHN",
  "event_type": "conflict",
  "days_back": 30,
  "max_goldstein": -2.0
}
```

---

### 2. `gdelt_gkg`
Query Global Knowledge Graph for entities and themes.

**Parameters:**
- `query` (str, optional): Text query to filter records (searches themes, persons, organizations)
- `themes` (list[str], optional): List of GKG theme codes (e.g., ["ENV_CLIMATECHANGE", "LEADER"])
- `days_back` (int, default=7): Number of days to look back (max: 365)

**Returns:** Aggregated summary with:
- Total record count
- Top 10 themes with counts
- Top 10 persons with counts
- Top 10 organizations with counts
- Average tone
- Date range

**Example:**
```json
{
  "query": "climate",
  "days_back": 14
}
```

---

### 3. `gdelt_actors`
Map actor relationships - who interacts with a given country.

**Parameters:**
- `country` (str): ISO3 country code (e.g., "USA", "RUS", "CHN")
- `relationship` (str, default="both"): Relationship type - "source" (country as actor1), "target" (as actor2), or "both"
- `days_back` (int, default=30): Number of days to look back (max: 365)

**Returns:** List of actor relationships with:
- Actor country code
- Relationship type
- Interaction count
- Average Goldstein scale
- Top 5 event codes with counts and names

**Example:**
```json
{
  "country": "UKR",
  "relationship": "both",
  "days_back": 60
}
```

---

### 4. `gdelt_trends`
Get coverage trends over time for a query.

**Parameters:**
- `query` (str): Search query string
- `metric` (str, default="volume"): Metric to track - "volume" (article count) or "tone" (average tone)
- `days_back` (int, default=30): Number of days to look back (max: 90)

**Returns:** Time series data with date and value for each point.

**Example:**
```json
{
  "query": "elections",
  "metric": "volume",
  "days_back": 30
}
```

---

### 5. `gdelt_doc`
Full-text article search via GDELT DOC API.

**Parameters:**
- `query` (str): Search query string (supports boolean operators, phrases)
- `days_back` (int, default=7): Number of days to look back (max: 90)
- `max_results` (int, default=100): Maximum results to return (1-250)
- `sort_by` (str, default="date"): Sort order - "date", "relevance", or "tone"

**Returns:** List of articles with url, title, tone, date, and language.

**Example:**
```json
{
  "query": "\"artificial intelligence\" AND regulation",
  "days_back": 14,
  "max_results": 50,
  "sort_by": "relevance"
}
```

---

### 6. `gdelt_cameo_lookup`
Look up CAMEO code meanings and Goldstein scale values.

**Parameters:**
- `code` (str, optional): Specific CAMEO code to look up (e.g., "14", "141", "20")
- `search` (str, optional): Text search in code names/descriptions

**Note:** Must provide either `code` or `search` parameter.

**Returns:** List of CAMEO code entries with:
- Code
- Name
- Description
- Goldstein scale value
- Quad class (1-4)
- Is conflict/cooperation flags

**Example:**
```json
{
  "search": "protest"
}
```

## CAMEO Event Codes

CAMEO codes classify events by type and intensity:

**Cooperation (01-08):**
- 01-05: Verbal cooperation (Quad class 1)
- 06-08: Material cooperation (Quad class 2)

**Conflict (14-20):**
- 09-13: Verbal conflict (Quad class 3)
- 14-20: Material conflict (Quad class 4)

**Goldstein Scale:** Ranges from -10 (most conflictual) to +10 (most cooperative).

## Common GKG Theme Codes

- `ENV_CLIMATECHANGE` - Climate change
- `LEADER` - Political leaders
- `PROTEST` - Protests and demonstrations
- `TERROR` - Terrorism
- `ECON_INFLATION` - Inflation
- `MANMADE_DISASTER_IMPLIED` - Man-made disasters

For full theme taxonomy, use the GDELT documentation or query the lookup endpoints.

## Architecture

- **Server Framework:** FastMCP (async MCP server)
- **Data Source:** py-gdelt library (unified GDELT client)
- **Design:** Single shared GDELTClient instance, async-first, structured JSON responses

## Error Handling

All tools handle errors gracefully:
- Invalid country codes → Pydantic validation error
- Invalid CAMEO codes → Validation error
- API failures → Clear error messages
- Empty results → Returns empty list/dict

## Performance Considerations

- Date ranges are capped (events: 365 days, DOC: 90 days, trends: 90 days)
- Result limits prevent overwhelming responses (events: 500, articles: 250, actors: 50)
- GDELT API rate limits apply - the server does not implement rate limiting
- BigQuery fallback available if configured in py-gdelt settings

## Development

### Linting
```bash
ruff check server.py
ruff format server.py
```

### Type Checking
```bash
mypy server.py
```

## License

MIT License (inherits from py-gdelt)
