from __future__ import annotations

from dataclasses import dataclass, field


# --- Claude plugin types ---


@dataclass
class ClaudeMcpServer:
    type: str | None = None
    command: str | None = None
    args: list[str] | None = None
    url: str | None = None
    cwd: str | None = None
    env: dict[str, str] | None = None
    headers: dict[str, str] | None = None


@dataclass
class ClaudeManifest:
    name: str
    version: str
    description: str | None = None
    author: dict[str, str] | None = None
    keywords: list[str] | None = None
    agents: str | list[str] | None = None
    commands: str | list[str] | None = None
    skills: str | list[str] | None = None
    hooks: str | list[str] | dict | None = None
    mcp_servers: dict[str, dict] | str | list[str] | None = None


@dataclass
class ClaudeAgent:
    name: str
    body: str
    source_path: str
    description: str | None = None
    capabilities: list[str] | None = None
    model: str | None = None


@dataclass
class ClaudeCommand:
    name: str
    body: str
    source_path: str
    description: str | None = None
    argument_hint: str | None = None
    model: str | None = None
    allowed_tools: list[str] | None = None
    disable_model_invocation: bool | None = None


@dataclass
class ClaudeSkill:
    name: str
    source_dir: str
    skill_path: str
    description: str | None = None
    argument_hint: str | None = None
    disable_model_invocation: bool | None = None


@dataclass
class ClaudeHookEntry:
    type: str
    command: str | None = None
    timeout: int | None = None
    prompt: str | None = None
    agent: str | None = None


@dataclass
class ClaudeHookMatcher:
    matcher: str | None = None
    hooks: list[ClaudeHookEntry] = field(default_factory=list)


@dataclass
class ClaudeHooks:
    hooks: dict[str, list[ClaudeHookMatcher]] = field(default_factory=dict)


@dataclass
class ClaudePlugin:
    root: str
    manifest: ClaudeManifest
    agents: list[ClaudeAgent] = field(default_factory=list)
    commands: list[ClaudeCommand] = field(default_factory=list)
    skills: list[ClaudeSkill] = field(default_factory=list)
    hooks: ClaudeHooks | None = None
    mcp_servers: dict[str, ClaudeMcpServer] | None = None


# --- Shared output types ---


@dataclass
class SkillDir:
    name: str
    source_dir: str


# --- Codex output types ---


@dataclass
class CodexInvocationTargets:
    prompt_targets: dict[str, str] = field(default_factory=dict)
    skill_targets: dict[str, str] = field(default_factory=dict)
    agent_targets: dict[str, str] = field(default_factory=dict)


@dataclass
class CodexPrompt:
    name: str
    content: str


@dataclass
class CodexGeneratedSkill:
    name: str
    content: str


@dataclass
class CodexBundle:
    prompts: list[CodexPrompt] = field(default_factory=list)
    skill_dirs: list[SkillDir] = field(default_factory=list)
    generated_skills: list[CodexGeneratedSkill] = field(default_factory=list)
    invocation_targets: CodexInvocationTargets | None = None
    mcp_servers: dict[str, ClaudeMcpServer] | None = None


# --- OpenCode output types ---


@dataclass
class OpenCodeMcpServer:
    type: str  # "local" | "remote"
    command: list[str] | None = None
    url: str | None = None
    environment: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    enabled: bool = True


@dataclass
class OpenCodeAgentFile:
    name: str
    content: str


@dataclass
class OpenCodeCommandFile:
    name: str
    content: str


@dataclass
class OpenCodePluginFile:
    name: str
    content: str


@dataclass
class OpenCodeConfig:
    schema: str | None = None
    mcp: dict[str, OpenCodeMcpServer] | None = None
    permission: dict | None = None
    tools: dict[str, bool] | None = None


@dataclass
class OpenCodeBundle:
    config: OpenCodeConfig
    agents: list[OpenCodeAgentFile] = field(default_factory=list)
    command_files: list[OpenCodeCommandFile] = field(default_factory=list)
    plugins: list[OpenCodePluginFile] = field(default_factory=list)
    skill_dirs: list[SkillDir] = field(default_factory=list)


# --- Pi output types ---


@dataclass
class PiPrompt:
    name: str
    content: str


@dataclass
class PiSkillDir:
    name: str
    source_dir: str


@dataclass
class PiGeneratedSkill:
    name: str
    content: str


@dataclass
class PiExtensionFile:
    name: str
    content: str


@dataclass
class PiMcporterServer:
    description: str | None = None
    base_url: str | None = None
    command: str | None = None
    args: list[str] | None = None
    env: dict[str, str] | None = None
    headers: dict[str, str] | None = None


@dataclass
class PiMcporterConfig:
    mcp_servers: dict[str, PiMcporterServer] = field(default_factory=dict)


@dataclass
class PiBundle:
    prompts: list[PiPrompt] = field(default_factory=list)
    skill_dirs: list[PiSkillDir] = field(default_factory=list)
    generated_skills: list[PiGeneratedSkill] = field(default_factory=list)
    extensions: list[PiExtensionFile] = field(default_factory=list)
    mcporter_config: PiMcporterConfig | None = None
