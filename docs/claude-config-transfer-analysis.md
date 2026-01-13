# Claude-Config Transfer Analysis

Analysis of what can be transferred from `claude-config` to `rbw-claude-code`.

## Repository Comparison

### Key Philosophical Differences

| Aspect | claude-config | rbw-claude-code |
|--------|---------------|-----------------|
| **Core Focus** | Workflow discipline & quality gates | Plugin marketplace & safety hooks |
| **Skill Architecture** | Python scripts with XML output, structured multi-step workflows | Markdown-based agents/commands with YAML frontmatter |
| **Quality Enforcement** | Built into workflow (TW/QR loops) | Hooks (pre/post tool use) |
| **Documentation Model** | Strict two-file pattern with token budgets | Flexible CLAUDE.md + README |

---

## What claude-config Has That rbw-claude-code Lacks

### 1. Rigorous Convention System

claude-config has 9 convention files with specific, enforceable rules:

| Convention | What It Provides | Transfer Value |
|------------|------------------|----------------|
| `temporal.md` | Rules against "change-relative" comments | **HIGH** - prevents AI slop like "Added mutex to fix..." |
| `diff-format.md` | Unified diff spec for plans | **HIGH** - missing from rbw-claude-code |
| `intent-markers.md` | `:PERF:`, `:UNSAFE:`, `:SCHEMA:` markers | **MEDIUM** - structured way to suppress checks |
| `severity.md` | MUST/SHOULD/COULD with de-escalation | **HIGH** - rbw-claude-code lacks severity taxonomy |
| `code-quality/baseline.md` | 17 atomic code smells | **HIGH** - far more detailed than anti-slop.md |
| `code-quality/coherence.md` | 8 repetition patterns with thresholds | **HIGH** - completely missing |
| `code-quality/drift.md` | 5 architectural issues | **HIGH** - completely missing |
| `documentation.md` | Strict CLAUDE.md/README format with token budgets | **MEDIUM** - more rigorous than current approach |

### 2. Multi-Step Workflow Skills

claude-config's skills have structured phases with Python orchestration:

| Skill | Steps | What It Does | Transfer Approach |
|-------|-------|--------------|-------------------|
| `refactor` | 7 | 11-dimension parallel analysis | Convert to agent + workflow command |
| `problem-analysis` | 5 | Root cause identification (NOT solutions) | Convert to agent |
| `solution-design` | 9 | 7-perspective parallel solution generation | Convert to agent |
| `codebase-analysis` | 4 | Systematic exploration | Enhance existing Explore agent |
| `doc-sync` | variable | Audit/sync CLAUDE.md + README.md | New skill |

### 3. Output Style Enforcement

`output-styles/direct.md` provides:
- No hedging/apologizing
- FORBIDDEN markdown patterns in prose
- "This won't work because... Alternative:... Proceed?" pattern

This could become a rule in `templates/rules/`.

### 4. Quality Review Loop Pattern

claude-config enforces review cycles:
- Technical Writer (clarity)
- Quality Reviewer (completeness)
- Loop until both pass

rbw-claude-code's `/workflows:review` is close but uses parallel agents instead of iterative loops.

---

## Framework Components Worth Considering

### Python Orchestration Library (`skills/lib/workflow/`)

claude-config has a reusable Python framework:
- `types.py`: AgentRole, Routing (Linear/Branch/Terminal), Step, QRState, GateConfig
- `formatters/xml.py`: 26 XML formatters for structured output
- `cli.py`: Standard argument parsing

**Transfer decision**: The XML-based structured output is powerful but adds complexity. rbw-claude-code's Markdown agent approach is simpler. Consider **hybrid**: use Python orchestration for complex multi-step skills only.

---

## What rbw-claude-code Has That Could Enhance claude-config

| Feature | Value |
|---------|-------|
| Hook system with bypass protection | Defense in depth |
| Plugin marketplace infrastructure | Distribution mechanism |
| Gemini integration | External LLM second opinions |
| Security hooks (git-safety-guard, safety-guard, etc.) | Production safety |
| Agent-native architecture philosophy | Modern AI patterns |

---

## Actionable Recommendations

### HIGH PRIORITY - Transfer These

1. **Conventions to add to `templates/rules/`**:
   - `temporal.md` → `templates/rules/temporal-contamination.md` (prevent change-relative comments)
   - `severity.md` → `templates/rules/severity-taxonomy.md` (MUST/SHOULD/COULD)
   - `code-quality/baseline.md` → `templates/rules/code-smells/baseline.md` (17 atomic smells)
   - `code-quality/coherence.md` → `templates/rules/code-smells/coherence.md` (8 patterns)
   - `code-quality/drift.md` → `templates/rules/code-smells/drift.md` (5 architectural issues)

2. **New Agents to create**:
   - `problem-analysis-agent` - Root cause identification (not solutions!)
   - `solution-design-agent` - Multi-perspective solution generation (7 perspectives in parallel)
   - `refactor-analyst-agent` - 11-dimension refactoring analysis

3. **Enhance existing agents**:
   - Add severity taxonomy to `code-simplicity-reviewer`
   - Add temporal contamination checks to code reviewers
   - Add coherence pattern detection to `pattern-recognition-specialist`

### MEDIUM PRIORITY - Consider These

1. **diff-format.md** → Use in `/workflows:plan` for structured code change specs

2. **intent-markers.md** → Add `:PERF:`, `:UNSAFE:`, `:SCHEMA:` marker support to reviewers

3. **direct.md output style** → `templates/rules/output-style-direct.md`

4. **doc-sync skill** → New skill for CLAUDE.md/README.md synchronization

### LOW PRIORITY - Nice to Have

1. Python orchestration framework - Only if complex multi-step skills needed
2. Token budget enforcement - Currently implicit in rbw-claude-code
3. QR iteration loops - Current parallel review approach is simpler

---

## Quick Wins (Lowest Effort, High Impact)

1. **Copy `temporal.md`** directly to `templates/rules/` - immediately improves comment quality
2. **Copy `code-quality/baseline.md`** - gives reviewers 17 specific patterns to check
3. **Add severity levels** to existing agent prompts - adds structure to reviews

---

## Summary

**claude-config** excels at:
- Rigorous conventions with specific, enforceable rules
- Multi-step workflow orchestration with quality gates
- Deep code quality checks (17 baseline + 8 coherence + 5 drift patterns)
- Temporal contamination prevention
- Severity taxonomy

**rbw-claude-code** excels at:
- Plugin marketplace infrastructure
- Safety hooks with bypass protection
- Simple Markdown-based agent/skill definitions
- Agent-native architecture philosophy
- External LLM integration (Gemini)

**Best transfer strategy**: Adopt claude-config's **conventions and detection patterns** while keeping rbw-claude-code's **simpler Markdown agent architecture**. The conventions are the real value - they're language-agnostic knowledge that can enhance any reviewer agent.

---

## Source Repositories

- **claude-config**: `/home/rbw/repo/claude-config`
- **rbw-claude-code**: `/home/rbw/repo/rbw-claude-code`

*Analysis generated: 2026-01-11*
