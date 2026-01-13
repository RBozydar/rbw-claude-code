# Temporal Contamination in Code Comments

Comments must be written from the perspective of a reader encountering the code for the first time, with no knowledge of what came before or how it got here. The code simply _is_.

**Why this matters**: Change-narrative comments are an LLM artifact -- a category error, not merely a style issue. The change process is ephemeral and irrelevant to the code's ongoing existence. Humans writing comments naturally describe what code IS, not what they DID to create it.

Think of it this way: a novel's narrator never describes the author's typing process. Similarly, code comments should never describe the developer's editing process.

## Detection Heuristic

Evaluate each comment against these five questions.

### 1. Does it describe an action taken rather than what exists?

**Category**: Change-relative

| Contaminated | Timeless Present |
| --- | --- |
| `// Added mutex to fix race condition` | `// Mutex serializes cache access from concurrent requests` |
| `// New validation for the edge case` | `// Rejects negative values (downstream assumes unsigned)` |
| `// Changed to use batch API` | `// Batch API reduces round-trips from N to 1` |

Signal words: "Added", "Replaced", "Now uses", "Changed to", "New", "Updated", "Refactored"

### 2. Does it compare to something not in the code?

**Category**: Baseline reference

| Contaminated | Timeless Present |
| --- | --- |
| `// Replaces per-tag logging with summary` | `// Single summary line; per-tag logging would produce 1500+ lines` |
| `// Unlike the old approach, this is thread-safe` | `// Thread-safe: each goroutine gets independent state` |
| `// Previously handled in caller` | `// Encapsulated here; caller should not manage lifecycle` |

Signal words: "Instead of", "Rather than", "Previously", "Replaces", "Unlike the old", "No longer"

### 3. Does it describe where to put code rather than what code does?

**Category**: Location directive

| Contaminated | Timeless Present |
| --- | --- |
| `// After the SendAsync call` | _(delete -- diff structure encodes location)_ |
| `// Insert before validation` | _(delete -- diff structure encodes location)_ |
| `// Add this at line 425` | _(delete -- diff structure encodes location)_ |

Signal words: "After", "Before", "Insert", "At line", "Here:", "Below", "Above"

**Action**: Always delete. Location is encoded in diff structure, not comments.

### 4. Does it describe intent rather than behavior?

**Category**: Planning artifact

| Contaminated | Timeless Present |
| --- | --- |
| `// TODO: add retry logic later` | _(delete, or implement retry now)_ |
| `// Will be extended for batch mode` | _(delete -- do not document hypothetical futures)_ |
| `// Temporary workaround until API v2` | `// API v1 lacks filtering; client-side filter required` |

Signal words: "Will", "TODO", "Planned", "Eventually", "For future", "Temporary", "Workaround until"

**Action**: Delete, implement the feature, or reframe as current constraint.

### 5. Does it describe the author's choice rather than code behavior?

**Category**: Intent leakage

| Contaminated | Timeless Present |
| --- | --- |
| `// Intentionally placed after validation` | `// Runs after validation completes` |
| `// Deliberately using mutex over channel` | `// Mutex serializes access (single-writer pattern)` |
| `// Chose polling for reliability` | `// Polling: 30% webhook delivery failures observed` |
| `// We decided to cache at this layer` | `// Cache here: reduces DB round-trips for hot path` |

Signal words: "intentionally", "deliberately", "chose", "decided", "on purpose", "by design", "we opted"

**Action**: Extract the technical justification; discard the decision narrative.

## Catch-All Rule

If a comment only makes sense to someone who knows the code's history, it is temporally contaminated -- even if it does not match any category above.

## Subtle Cases

Same word, different verdict -- detection requires semantic judgment, not keyword matching.

| Comment | Verdict | Reasoning |
| --- | --- | --- |
| `// Now handles edge cases properly` | Contaminated | "properly" implies it was improper before |
| `// Now blocks until connection ready` | Clean | "now" describes runtime moment, not code history |
| `// Fixed the null pointer issue` | Contaminated | Describes a fix, not behavior |
| `// Returns null when key not found` | Clean | Describes behavior |

## The Transformation Pattern

> **Extract the technical justification, discard the change narrative.**

1. What useful info is buried? (problem, behavior)
2. Reframe as timeless present

Example: "Added mutex to fix race" -> "Mutex serializes concurrent access"
