"""GDELT MCP Server for geopolitical research.

This MCP server exposes the py-gdelt library capabilities as structured tools
for AI agents to query GDELT data sources (Events, GKG, DOC API, etc.).
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from py_gdelt import GDELTClient
from py_gdelt.filters import DateRange, DocFilter, EventFilter, GKGFilter
from py_gdelt.lookups.cameo import CAMEOCodes
from py_gdelt.models.articles import Article
from py_gdelt.models.events import Event
from py_gdelt.models.gkg import GKGRecord


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for tool responses


class EventSummary(BaseModel):
    """Summary of a GDELT event."""

    global_event_id: int
    date: str
    actor1_country: str | None
    actor1_name: str | None
    actor2_country: str | None
    actor2_name: str | None
    event_code: str
    event_name: str | None
    goldstein_scale: float
    avg_tone: float
    source_url: str | None


class GKGSummary(BaseModel):
    """Summary of GKG entity and theme data."""

    total_records: int
    top_themes: list[tuple[str, int]]
    top_persons: list[tuple[str, int]]
    top_organizations: list[tuple[str, int]]
    avg_tone: float
    date_range: str


class ActorRelationship(BaseModel):
    """Actor relationship summary."""

    actor: str
    relationship_type: str  # "source" | "target" | "both"
    interaction_count: int
    avg_goldstein: float
    top_event_codes: list[tuple[str, int]]


class TrendPoint(BaseModel):
    """Single point in a trend time series."""

    date: str
    value: float


class ArticleSummary(BaseModel):
    """Summary of a GDELT article."""

    url: str
    title: str | None
    seendate: str
    tone: float | None
    language: str | None


# Initialize MCP server
mcp = FastMCP("GDELT Research Server")


# Shared GDELT client (initialized on first use)
_client: GDELTClient | None = None
_cameo_codes: CAMEOCodes | None = None


async def get_client() -> GDELTClient:
    """Get or create the shared GDELT client."""
    global _client
    if _client is None:
        _client = GDELTClient()
        await _client._initialize()
    return _client


def get_cameo_codes() -> CAMEOCodes:
    """Get or create the shared CAMEO codes lookup."""
    global _cameo_codes
    if _cameo_codes is None:
        _cameo_codes = CAMEOCodes()
    return _cameo_codes


@mcp.tool()
async def gdelt_events(
    actor1_country: str | None = None,
    actor2_country: str | None = None,
    event_type: str = "all",
    days_back: int = 7,
    min_goldstein: float | None = None,
    max_goldstein: float | None = None,
) -> list[dict[str, Any]]:
    """Query CAMEO-coded events from GDELT.

    Searches for events matching actor and event type criteria.
    Returns structured event data with actors, event codes, Goldstein scale, tone, etc.

    Args:
        actor1_country: ISO3 country code for actor 1 (e.g., "USA", "RUS", "CHN")
        actor2_country: ISO3 country code for actor 2
        event_type: Type filter - "conflict" (codes 14-20), "cooperation" (01-08), or "all"
        days_back: Number of days to look back (default: 7, max: 365)
        min_goldstein: Minimum Goldstein scale (-10 to 10, negative=conflict)
        max_goldstein: Maximum Goldstein scale (-10 to 10, positive=cooperation)

    Returns:
        List of event summaries with global_event_id, actors, event details, and source URLs
    """
    client = await get_client()
    cameo = get_cameo_codes()

    # Build date range
    end_date = date.today() - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=min(days_back, 365))

    # Build filter
    event_filter = EventFilter(
        date_range=DateRange(start=start_date, end=end_date),
        actor1_country=actor1_country,
        actor2_country=actor2_country,
    )

    # Query events
    logger.info(
        "Querying events: actor1=%s, actor2=%s, type=%s, days=%d",
        actor1_country,
        actor2_country,
        event_type,
        days_back,
    )
    events = await client.events.query(event_filter)

    # Filter by event type
    filtered_events: list[Event] = []
    for event in events:
        # Apply Goldstein filter
        if min_goldstein is not None and event.goldstein_scale < min_goldstein:
            continue
        if max_goldstein is not None and event.goldstein_scale > max_goldstein:
            continue

        # Apply event type filter
        if event_type == "conflict":
            if not cameo.is_conflict(event.event_code):
                continue
        elif event_type == "cooperation":
            if not cameo.is_cooperation(event.event_code):
                continue

        filtered_events.append(event)

    # Convert to summaries
    results: list[dict[str, Any]] = []
    for event in filtered_events[:500]:  # Limit to 500 results
        cameo_entry = cameo.get(event.event_code)
        event_name = cameo_entry.name if cameo_entry else None

        results.append(
            {
                "global_event_id": event.global_event_id,
                "date": event.date.isoformat(),
                "actor1_country": event.actor1.country_code if event.actor1 else None,
                "actor1_name": event.actor1.name if event.actor1 else None,
                "actor2_country": event.actor2.country_code if event.actor2 else None,
                "actor2_name": event.actor2.name if event.actor2 else None,
                "event_code": event.event_code,
                "event_name": event_name,
                "goldstein_scale": event.goldstein_scale,
                "avg_tone": event.avg_tone,
                "source_url": event.source_url,
            }
        )

    logger.info("Returning %d events", len(results))
    return results


@mcp.tool()
async def gdelt_gkg(
    query: str | None = None,
    themes: list[str] | None = None,
    days_back: int = 7,
) -> dict[str, Any]:
    """Query Global Knowledge Graph for entities and themes.

    Searches GKG records and aggregates extracted themes, persons, organizations, and tone.

    Args:
        query: Text query to filter records (searches themes, persons, organizations)
        themes: List of GKG theme codes to filter by (e.g., ["ENV_CLIMATECHANGE", "LEADER"])
        days_back: Number of days to look back (default: 7, max: 365)

    Returns:
        Aggregated summary with top themes, entities, and tone analysis
    """
    client = await get_client()

    # Build date range
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=min(days_back, 365))

    # Build filter
    gkg_filter = GKGFilter(
        date_range=DateRange(start=start_date, end=end_date),
        themes=themes,
    )

    # Query GKG
    logger.info("Querying GKG: query=%s, themes=%s, days=%d", query, themes, days_back)
    records = await client.gkg.query(gkg_filter)

    # Filter by text query if provided
    if query:
        query_lower = query.lower()
        filtered_records: list[GKGRecord] = []
        for record in records:
            # Check if query matches themes, persons, or organizations
            match = False
            for theme in record.themes:
                if query_lower in theme.name.lower():
                    match = True
                    break
            if not match:
                for person in record.persons:
                    if query_lower in person.name.lower():
                        match = True
                        break
            if not match:
                for org in record.organizations:
                    if query_lower in org.name.lower():
                        match = True
                        break
            if match:
                filtered_records.append(record)
        records = filtered_records

    # Aggregate entities
    theme_counts: dict[str, int] = {}
    person_counts: dict[str, int] = {}
    org_counts: dict[str, int] = {}
    total_tone = 0.0
    tone_count = 0

    for record in records:
        for theme in record.themes:
            theme_counts[theme.name] = theme_counts.get(theme.name, 0) + 1
        for person in record.persons:
            person_counts[person.name] = person_counts.get(person.name, 0) + 1
        for org in record.organizations:
            org_counts[org.name] = org_counts.get(org.name, 0) + 1
        if record.tone:
            total_tone += record.tone.tone
            tone_count += 1

    # Sort and get top items
    top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_persons = sorted(person_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_orgs = sorted(org_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    avg_tone = total_tone / tone_count if tone_count > 0 else 0.0

    result = {
        "total_records": len(records),
        "top_themes": [{"name": name, "count": count} for name, count in top_themes],
        "top_persons": [{"name": name, "count": count} for name, count in top_persons],
        "top_organizations": [{"name": name, "count": count} for name, count in top_orgs],
        "avg_tone": avg_tone,
        "date_range": f"{start_date.isoformat()} to {end_date.isoformat()}",
    }

    logger.info("Returning GKG summary: %d records", len(records))
    return result


@mcp.tool()
async def gdelt_actors(
    country: str,
    relationship: str = "both",
    days_back: int = 30,
) -> list[dict[str, Any]]:
    """Map actor relationships - who interacts with a given country.

    Analyzes events to find which actors/countries interact with the specified country.

    Args:
        country: ISO3 country code (e.g., "USA", "RUS", "CHN")
        relationship: Relationship type - "source" (country as actor1), "target" (as actor2), or "both"
        days_back: Number of days to look back (default: 30, max: 365)

    Returns:
        List of actor relationships with interaction counts, avg Goldstein scale, and top event types
    """
    client = await get_client()
    cameo = get_cameo_codes()

    # Build date range
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=min(days_back, 365))

    # Query events where country is actor1 or actor2
    results: list[dict[str, Any]] = []

    if relationship in ("source", "both"):
        # Country as actor1 (source)
        filter1 = EventFilter(
            date_range=DateRange(start=start_date, end=end_date),
            actor1_country=country,
        )
        events1 = await client.events.query(filter1)

        # Aggregate by actor2
        actor_stats: dict[str, dict[str, Any]] = {}
        for event in events1:
            if not event.actor2 or not event.actor2.country_code:
                continue
            actor = event.actor2.country_code
            if actor not in actor_stats:
                actor_stats[actor] = {
                    "count": 0,
                    "goldstein_sum": 0.0,
                    "event_codes": {},
                }
            actor_stats[actor]["count"] += 1
            actor_stats[actor]["goldstein_sum"] += event.goldstein_scale
            code = event.event_code
            actor_stats[actor]["event_codes"][code] = (
                actor_stats[actor]["event_codes"].get(code, 0) + 1
            )

        # Convert to results
        for actor, stats in actor_stats.items():
            top_codes = sorted(stats["event_codes"].items(), key=lambda x: x[1], reverse=True)[:5]
            results.append(
                {
                    "actor": actor,
                    "relationship_type": "source",
                    "interaction_count": stats["count"],
                    "avg_goldstein": stats["goldstein_sum"] / stats["count"],
                    "top_event_codes": [
                        {
                            "code": code,
                            "count": count,
                            "name": entry.name if (entry := cameo.get(code)) else None,
                        }
                        for code, count in top_codes
                    ],
                }
            )

    if relationship in ("target", "both"):
        # Country as actor2 (target)
        filter2 = EventFilter(
            date_range=DateRange(start=start_date, end=end_date),
            actor2_country=country,
        )
        events2 = await client.events.query(filter2)

        # Aggregate by actor1
        actor_stats = {}
        for event in events2:
            if not event.actor1 or not event.actor1.country_code:
                continue
            actor = event.actor1.country_code
            if actor not in actor_stats:
                actor_stats[actor] = {
                    "count": 0,
                    "goldstein_sum": 0.0,
                    "event_codes": {},
                }
            actor_stats[actor]["count"] += 1
            actor_stats[actor]["goldstein_sum"] += event.goldstein_scale
            code = event.event_code
            actor_stats[actor]["event_codes"][code] = (
                actor_stats[actor]["event_codes"].get(code, 0) + 1
            )

        # Convert to results
        for actor, stats in actor_stats.items():
            top_codes = sorted(stats["event_codes"].items(), key=lambda x: x[1], reverse=True)[:5]
            results.append(
                {
                    "actor": actor,
                    "relationship_type": "target",
                    "interaction_count": stats["count"],
                    "avg_goldstein": stats["goldstein_sum"] / stats["count"],
                    "top_event_codes": [
                        {
                            "code": code,
                            "count": count,
                            "name": entry.name if (entry := cameo.get(code)) else None,
                        }
                        for code, count in top_codes
                    ],
                }
            )

    # Sort by interaction count
    results.sort(key=lambda x: x["interaction_count"], reverse=True)

    logger.info("Returning %d actor relationships for %s", len(results), country)
    return results[:50]  # Limit to top 50


@mcp.tool()
async def gdelt_trends(
    query: str,
    metric: str = "volume",
    days_back: int = 30,
) -> list[dict[str, Any]]:
    """Get coverage trends over time for a query.

    Analyzes article volume or tone trends for a search query over time.

    Args:
        query: Search query string
        metric: Metric to track - "volume" (article count) or "tone" (average tone)
        days_back: Number of days to look back (default: 30, max: 90)

    Returns:
        Time series data with date and value for each point
    """
    client = await get_client()

    # Limit to 90 days for timeline queries
    days = min(days_back, 90)

    # Use DOC API timeline mode
    timespan = f"{days}d"

    logger.info("Querying trends: query=%s, metric=%s, days=%d", query, metric, days)

    if metric == "volume":
        # Get timeline data
        timeline = await client.doc.timeline(query, timespan=timespan)

        # Convert to trend points
        results = [{"date": point.date, "value": float(point.value)} for point in timeline.points]

    else:  # tone
        # For tone, we need to query articles and aggregate by date
        doc_filter = DocFilter(
            query=query,
            timespan=timespan,
            max_results=250,  # API limit
            sort_by="date",
        )
        articles = await client.doc.query(doc_filter)

        # Group by date and calculate average tone
        date_tones: dict[str, list[float]] = {}
        for article in articles:
            if article.tone is not None and article.seendate:
                date_str = article.seendate[:8]  # YYYYMMDD
                if date_str not in date_tones:
                    date_tones[date_str] = []
                date_tones[date_str].append(article.tone)

        # Calculate averages
        results = []
        for date_str, tones in sorted(date_tones.items()):
            avg_tone = sum(tones) / len(tones) if tones else 0.0
            # Format date as YYYY-MM-DD
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            results.append({"date": formatted_date, "value": avg_tone})

    logger.info("Returning %d trend points", len(results))
    return results


@mcp.tool()
async def gdelt_doc(
    query: str,
    days_back: int = 7,
    max_results: int = 100,
    sort_by: str = "date",
) -> list[dict[str, Any]]:
    """Full-text article search via GDELT DOC API.

    Search for news articles matching a query across GDELT's monitored sources.

    Args:
        query: Search query string (supports boolean operators, phrases)
        days_back: Number of days to look back (default: 7, max: 90)
        max_results: Maximum results to return (1-250, default: 100)
        sort_by: Sort order - "date", "relevance", or "tone" (default: "date")

    Returns:
        List of articles with url, title, tone, date, and language
    """
    client = await get_client()

    # Build timespan
    days = min(days_back, 90)
    timespan = f"{days}d"

    # Validate sort_by
    if sort_by not in ("date", "relevance", "tone"):
        sort_by = "date"

    logger.info(
        "Searching articles: query=%s, days=%d, max=%d, sort=%s",
        query,
        days,
        max_results,
        sort_by,
    )

    articles: list[Article] = await client.doc.search(
        query=query,
        timespan=timespan,
        max_results=min(max_results, 250),
        sort_by=sort_by,  # type: ignore[arg-type]
    )

    # Convert to summaries
    results = [
        {
            "url": article.url,
            "title": article.title,
            "seendate": article.seendate,
            "tone": article.tone,
            "language": article.language,
        }
        for article in articles
    ]

    logger.info("Returning %d articles", len(results))
    return results


@mcp.tool()
async def gdelt_cameo_lookup(
    code: str | None = None,
    search: str | None = None,
) -> list[dict[str, Any]]:
    """Look up CAMEO code meanings and Goldstein scale values.

    Search or retrieve CAMEO event codes with their descriptions and conflict/cooperation scores.

    Args:
        code: Specific CAMEO code to look up (e.g., "14", "141", "20")
        search: Text search in code names/descriptions (substring match)

    Returns:
        List of CAMEO code entries with code, name, description, and Goldstein scale
    """
    cameo = get_cameo_codes()

    results: list[dict[str, Any]] = []

    if code:
        # Look up specific code
        entry = cameo.get(code)
        if entry:
            goldstein = cameo.get_goldstein(code)
            results.append(
                {
                    "code": code,
                    "name": entry.name,
                    "description": entry.description,
                    "goldstein_scale": goldstein.value if goldstein else None,
                    "quad_class": cameo.get_quad_class(code),
                    "is_conflict": cameo.is_conflict(code),
                    "is_cooperation": cameo.is_cooperation(code),
                }
            )

    elif search:
        # Search codes
        matching_codes = cameo.search(search)
        for matching_code in matching_codes[:20]:  # Limit to 20 results
            entry = cameo.get(matching_code)
            if entry:
                goldstein = cameo.get_goldstein(matching_code)
                results.append(
                    {
                        "code": matching_code,
                        "name": entry.name,
                        "description": entry.description,
                        "goldstein_scale": goldstein.value if goldstein else None,
                        "quad_class": cameo.get_quad_class(matching_code),
                        "is_conflict": cameo.is_conflict(matching_code),
                        "is_cooperation": cameo.is_cooperation(matching_code),
                    }
                )

    else:
        # Return error - need either code or search
        msg = "Must provide either 'code' or 'search' parameter"
        raise ValueError(msg)

    logger.info("Returning %d CAMEO code entries", len(results))
    return results


# Entry point
if __name__ == "__main__":
    mcp.run()
