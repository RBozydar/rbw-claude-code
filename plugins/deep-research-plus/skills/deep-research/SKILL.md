---
name: deep-research
description: Perform comprehensive research using the diffusion research loop - parallel worker agents, iterative gap detection, and structured synthesis. Use when you need thorough, multi-perspective research with citations.
---

<objective>
Execute deep, comprehensive research on any topic using a multi-agent diffusion loop:
1. Break down the query into research dimensions
2. Spawn parallel worker agents to research each dimension independently
3. Synthesize findings into a coherent draft
4. Use gap detection agent to identify missing coverage
5. Iterate until coverage is sufficient
6. Produce a final report with full citations
</objective>

<essential_principles>
## The Diffusion Research Pattern

This skill implements **Self-Balancing Test-Time Diffusion** - starting with a noisy/speculative understanding and iteratively refining through parallel, isolated research workers.

### Key Design Principles

1. **Worker Isolation**: Each research worker receives ONLY their assigned topic. They cannot see:
   - Other workers' findings
   - The current draft
   - The full research brief
   This prevents herd behavior and ensures diverse perspectives.

2. **Gap Detection Objectivity**: Use a separate gap-detector agent (not yourself) to evaluate coverage. This avoids the bias of judging your own work.

3. **Conservative Iteration**: Continue researching if:
   - Coverage < 70% of core questions
   - Any critical question is unanswered
   Stop when diminishing returns are reached.

4. **Quality Over Quantity**: 3-5 well-sourced findings per worker beats 10 weakly-sourced ones.
</essential_principles>

<algorithm>
## The Research Loop

```
PHASE 0: REFINEMENT (Interactive)
├── 0.1 Parse user query
├── 0.2 Generate DRAFT research brief
├── 0.3 Present brief to user via AskUserQuestion
│   ├── "Are these dimensions correct?"
│   ├── "Any areas to add or remove?"
│   └── "What depth/focus do you need?"
├── 0.4 Refine brief based on feedback
└── 0.5 Confirm and proceed

PHASE 1: INITIALIZATION
├── 1.1 Finalize research brief from refinement
└── 1.2 Generate initial speculative draft (noisy starting point)

PHASE 2: DIFFUSION LOOP (max 3 iterations)
├── 2.1 SPAWN WORKERS
│   ├── Identify 2-5 research topics from brief/gaps
│   ├── Launch research-worker agents in PARALLEL
│   └── Collect findings (wait for all to complete)
│
├── 2.2 SYNTHESIZE
│   ├── Merge worker findings into current draft
│   ├── Resolve contradictions
│   └── Structure with citations
│
├── 2.3 GAP DETECTION
│   ├── Launch gap-detector agent with: query, brief, draft
│   ├── Receive coverage score and gap topics
│   └── Decision: CONTINUE (spawn more workers) or COMPLETE
│
└── 2.4 ITERATE or EXIT

PHASE 3: FINAL REPORT
├── 3.1 Polish synthesis into final report
├── 3.2 Compile all sources with descriptions
└── 3.3 Add executive summary
```

## Execution Modes

**Interactive (default):** Main Claude orchestrates, can ask questions and steer mid-research.

**Background:** Spawn an orchestrator subagent for autonomous "fire and forget" research. Use when user wants to continue other work. See workflows/background-research.md.
</algorithm>

<intake>
What would you like me to research?

Provide your research question or topic. I will:
1. Break it down into researchable dimensions
2. Deploy parallel research agents
3. Synthesize findings with citations
4. Iterate until comprehensive coverage

**Example queries:**
- "What are the latest developments in quantum computing for drug discovery?"
- "Compare the architectural approaches of major LLM providers"
- "How are companies implementing AI governance frameworks?"
</intake>

<execution_guide>
## How to Execute This Skill

### Phase 0: Refinement (Interactive)

After receiving the query, generate a DRAFT brief and validate with the user.

**Step 1: Generate Draft Brief**

```markdown
## Draft Research Brief

**Your Query:** [User's original question]

**Proposed Dimensions:**
1. [Dimension 1] - [Why it matters]
2. [Dimension 2] - [Why it matters]
3. [Dimension 3] - [Why it matters]

**Key Questions I Plan to Answer:**
- [Question 1] (Core)
- [Question 2] (Core)
- [Question 3] (Supporting)
```

**Step 2: Validate with User via AskUserQuestion**

```
AskUserQuestion(
  questions: [
    {
      header: "Dimensions",
      question: "Are these research dimensions correct for your needs?",
      options: [
        { label: "Yes, proceed", description: "These dimensions cover what I need" },
        { label: "Add more", description: "I want to add additional dimensions" },
        { label: "Remove some", description: "Some dimensions aren't relevant" },
        { label: "Rethink entirely", description: "Let's approach this differently" }
      ],
      multiSelect: false
    },
    {
      header: "Depth",
      question: "What level of depth do you need?",
      options: [
        { label: "Quick overview", description: "Key facts, 1 iteration, ~2 min" },
        { label: "Standard (Recommended)", description: "Thorough coverage, 2-3 iterations, ~5 min" },
        { label: "Exhaustive", description: "Maximum depth, all angles, ~10 min" }
      ],
      multiSelect: false
    },
    {
      header: "Focus",
      question: "Any specific focus areas or constraints?",
      options: [
        { label: "No constraints", description: "Research broadly across all dimensions" },
        { label: "Recent only", description: "Focus on developments from last 1-2 years" },
        { label: "Practical focus", description: "Prioritize actionable/implementation info" },
        { label: "Academic focus", description: "Prioritize research papers and studies" }
      ],
      multiSelect: true
    }
  ]
)
```

**Step 3: Refine Based on Feedback**

- If user selects "Add more" → ask what to add
- If user selects "Remove some" → ask what to remove
- If user selects "Rethink entirely" → regenerate brief with new approach
- Adjust depth and focus based on selections
- Proceed to Phase 1 once confirmed

### Phase 1: Generate Research Brief

After refinement, finalize the research brief:

```markdown
## Research Brief

**Query:** [User's original question]

**Core Dimensions:**
1. [Dimension 1] - [Why it matters]
2. [Dimension 2] - [Why it matters]
3. [Dimension 3] - [Why it matters]

**Key Questions:**
- [Question 1] (Core)
- [Question 2] (Core)
- [Question 3] (Supporting)
- [Question 4] (Supporting)
- [Question 5] (Contextual)

**Initial Topics for Workers:**
1. [Topic for Worker 1]
2. [Topic for Worker 2]
3. [Topic for Worker 3]
```

### Phase 2a: Spawn Workers

Use the Task tool to spawn research-worker agents **in parallel**:

```
Task(
  subagent_type: "deep_research:research-worker",
  prompt: "Research this topic: [TOPIC]

Context: This is part of a larger research effort on: [MAIN QUERY]

Focus on: [SPECIFIC ASPECTS TO COVER]

Return structured findings with citations.",
  description: "Research: [short topic]",
  run_in_background: false  # Wait for results
)
```

**CRITICAL**: Spawn ALL workers in a SINGLE message with multiple Task tool calls. This enables true parallel execution.

### Phase 2b: Synthesize Findings

After workers return, synthesize into a draft:

```markdown
## Research Draft (Iteration N)

### [Theme 1]

[Synthesized content from relevant worker findings]

Sources:
- [1] [URL]
- [2] [URL]

### [Theme 2]

[Synthesized content...]

### Current Gaps

[Note any obvious gaps before formal gap detection]
```

### Phase 2c: Gap Detection

Spawn the gap-detector agent:

```
Task(
  subagent_type: "deep_research:gap-detector",
  prompt: "Evaluate research coverage:

ORIGINAL QUERY:
[Query]

RESEARCH BRIEF:
[Brief]

CURRENT FINDINGS:
[Draft]

ITERATION: [N]

Assess coverage and identify gaps for follow-up.",
  description: "Detect research gaps"
)
```

### Phase 2d: Iterate or Complete

If gap-detector returns CONTINUE:
- Extract the gap topics
- Spawn new workers for those specific gaps
- Repeat synthesis and gap detection

If gap-detector returns COMPLETE:
- Move to Phase 3

**Maximum 3 iterations** to prevent infinite loops.

### Phase 3: Final Report

Structure the final output:

```markdown
# Research Report: [Title]

## Executive Summary

[3-5 bullet points of key findings]

## Key Findings

### [Finding 1]

[Detailed explanation with context]

**Sources:** [1], [2]

### [Finding 2]

[Detailed explanation...]

## Analysis

[Cross-cutting insights, patterns, implications]

## Limitations

[What couldn't be determined, areas of uncertainty]

## Sources

[1] [Title](URL) - [Description]
[2] [Title](URL) - [Description]
...

---
*Research conducted using diffusion research methodology with [N] parallel workers over [M] iterations.*
```
</execution_guide>

<worker_management>
## Managing Research Workers

### Spawning Pattern

Always spawn workers in parallel using a single message with multiple Task calls:

```
[In a single response, include multiple Task tool invocations:]

Task 1: "Research: quantum computing applications"
Task 2: "Research: drug discovery AI methods"
Task 3: "Research: current clinical trials"
```

### Worker Prompt Template

```
You are researching: [SPECIFIC TOPIC]

This is part of a larger investigation into: [MAIN QUERY]

Your focus areas:
- [Specific aspect 1]
- [Specific aspect 2]
- [Specific aspect 3]

Requirements:
- Use WebSearch for discovery, WebFetch for deep content
- Cite every factual claim with source URLs
- Return 3-7 key findings with confidence levels
- Note any contradictions or debates in the field
- Stop when you have sufficient coverage (5-7 searches max)

Do not research topics outside your assigned focus.
```

### Handling Worker Failures

If a worker returns an error or incomplete results:
- Note the gap in synthesis
- The gap detector will flag it for follow-up
- Do not block other workers
</worker_management>

<output_format>
## Final Report Structure

The report should be saved to a file and include:

1. **Metadata Header**
   - Query
   - Date
   - Iterations performed
   - Workers spawned

2. **Executive Summary** (bullet points, 100-200 words)

3. **Key Findings** (3-7 major findings with sources)

4. **Detailed Analysis** (cross-cutting themes, implications)

5. **Methodology Note** (brief explanation of research process)

6. **Complete Source List** (all URLs with descriptions)

Save to: `research_output/[topic-slug]_[date].md`
</output_format>

<success_criteria>
Research is complete when:
- All core questions from the brief are addressed
- Coverage score >= 70% (from gap detector)
- Key findings are well-sourced (2+ citations each)
- Contradictions are noted and explained
- Maximum 3 iterations reached

Research is NOT complete just because:
- The draft "reads well"
- You feel satisfied with the findings
- Workers stopped returning new information

Always use the gap-detector agent for objective evaluation.
</success_criteria>

<quick_start>
## Quick Start

1. User provides research query
2. Generate DRAFT research brief
3. **Use AskUserQuestion to validate dimensions, depth, focus**
4. Refine brief based on feedback
5. Spawn 2-4 research-worker agents in parallel
6. Synthesize findings into draft
7. Spawn gap-detector agent
8. If gaps found: spawn more workers for gap topics, repeat
9. If complete: generate final report

**Time expectation:** 2-5 minutes depending on depth and iterations

**Skip refinement:** If user explicitly says "just do it" or "skip questions", proceed directly with your best judgment on the brief.
</quick_start>

<mid_research_steering>
## Mid-Research Steering

During the diffusion loop, watch for user messages that indicate steering:

| User Says | Action |
|-----------|--------|
| "Focus more on X" | Add X-related topics to next worker batch |
| "Skip Y" | Remove Y from remaining work, note as out-of-scope |
| "Go deeper on Z" | Spawn additional worker specifically for Z |
| "That's enough" | Skip remaining iterations, move to final report |
| "Add dimension W" | Update brief, spawn worker for W |

Use AskUserQuestion if steering intent is ambiguous:

```
AskUserQuestion(
  questions: [{
    header: "Clarify",
    question: "You mentioned focusing on X. Should I...",
    options: [
      { label: "Add worker for X", description: "Research X specifically in next round" },
      { label: "Prioritize X in synthesis", description: "Weight X findings more heavily" },
      { label: "Replace other dimensions", description: "Drop less relevant dimensions for X" }
    ],
    multiSelect: false
  }]
)
```
</mid_research_steering>
