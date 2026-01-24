#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["cchooks"]
# ///
"""PreToolUse hook to block destructive file operations and supply chain attacks."""

import re

from cchooks import PreToolUseContext, create_context


c = create_context()
assert isinstance(c, PreToolUseContext)

if c.tool_name != "Bash":
    c.output.exit_success()

command = c.tool_input.get("command", "")

# Safe patterns - allow these
SAFE_PATTERNS = [
    r"rm\s+-rf\s+(/tmp/|/var/tmp/|\$TMPDIR/|\${TMPDIR}/)",
    r"rm\s+-fr\s+(/tmp/|/var/tmp/|\$TMPDIR/|\${TMPDIR}/)",
]

# Destructive patterns - block these
BLOCKED_PATTERNS = [
    # ==========================================================================
    # File destruction via rm
    # ==========================================================================
    (r"rm\s+(-[rRf]+\s+)+", "rm -rf is destructive outside temp directories"),
    (r"shred\s+", "shred permanently destroys file data"),
    (r"truncate\s+", "truncate destroys file contents"),
    # ==========================================================================
    # Data destruction via dd
    # ==========================================================================
    (r"\bdd\s+.*?\bof=", "dd with of= can overwrite/destroy disk data"),
    (r"\bdd\s+.*?\bif=/dev/zero", "dd from /dev/zero overwrites data with zeros"),
    (
        r"\bdd\s+.*?\bif=/dev/random",
        "dd from /dev/random overwrites data with random bytes",
    ),
    # ==========================================================================
    # In-place file modification via sed (without backup)
    # ==========================================================================
    # Allow sed -i.bak or sed -i'.bak' (with backup suffix) - these are safe
    # Block sed -i without suffix (no backup = destructive)
    # Must catch both: sed -i 's/...' (with space) and sed -i's/...' (no space)
    (
        r"\bsed\s+-i(?:\s+(?!\.)|'s|s)",
        "sed -i without backup suffix is destructive (use sed -i.bak instead)",
    ),
    (
        r"\bsed\s+--in-place(?!=)",
        "sed --in-place without backup is destructive (use --in-place=.bak)",
    ),
    # ==========================================================================
    # File destruction via mv to /dev/null
    # ==========================================================================
    (r"\bmv\s+.*?/dev/null\b", "mv to /dev/null destroys files"),
    # ==========================================================================
    # find: Block file deletion and destructive exec patterns
    # ==========================================================================
    (r"find\s+.*?-delete", "find -delete permanently removes files"),
    (r"find\s+.*?-exec\s+rm\b", "find -exec rm permanently removes files"),
    (r"find\s+.*?-execdir\s+rm\b", "find -execdir rm permanently removes files"),
    (r"find\s+.*?-exec\s+shred\b", "find -exec shred permanently destroys files"),
    (
        r"find\s+.*?-exec\s+chmod\s+000",
        "find -exec chmod 000 removes all permissions",
    ),
    (
        r"find\s+.*?-exec\s+mv\s+.*?/dev/null\b",
        "find -exec mv to /dev/null destroys files",
    ),
    # ==========================================================================
    # xargs: Block piping to destructive commands
    # ==========================================================================
    (r"\|\s*xargs\s+rm\b", "xargs rm permanently removes files"),
    (
        r"\|\s*xargs\s+-[^\s]*\s+rm\b",
        "xargs with flags to rm permanently removes files",
    ),
    (r"\|\s*xargs\s+shred\b", "xargs shred permanently destroys files"),
    (r"\|\s*xargs\s+chmod\s+000", "xargs chmod 000 removes all permissions"),
    (r"\|\s*xargs\s+[^|]*\brm\s+-rf\b", "xargs with rm -rf is destructive"),
    # ==========================================================================
    # chmod: Block dangerous permission changes
    # ==========================================================================
    (r"chmod\s+000\s", "chmod 000 removes all permissions"),
    (r"chmod\s+777\s+.*\.ssh", "chmod 777 on .ssh is a security risk"),
    (r"chmod\s+777\s+.*\.env", "chmod 777 on .env is a security risk"),
    (r"chmod\s+-R\s+000", "chmod -R 000 recursively removes all permissions"),
    # ==========================================================================
    # Supply chain attacks
    # ==========================================================================
    (
        r"(curl|wget)\s+.{0,1000}?\|\s*(ba|z)?sh",
        "piping curl/wget to a shell is a supply chain attack vector",
    ),
    # ==========================================================================
    # Python/Perl one-liners for file destruction
    # ==========================================================================
    (
        r"python[23]?\s+-c\s+['\"].*os\.(remove|unlink|rmdir|rmtree)",
        "Python one-liner with file deletion detected",
    ),
    (
        r"python[23]?\s+-c\s+['\"].*shutil\.rmtree",
        "Python one-liner with recursive deletion detected",
    ),
    (
        r"python[23]?\s+-c\s+['\"].*pathlib.*\.(unlink|rmdir)",
        "Python one-liner with pathlib deletion detected",
    ),
    # ==========================================================================
    # Python one-liner obfuscation patterns
    # ==========================================================================
    (
        r"python[23]?\s+-c\s+['\"].*__import__\(['\"]os['\"].*\.(remove|unlink|rmdir)",
        "Python one-liner using __import__ with file deletion detected",
    ),
    (
        r"python[23]?\s+-c\s+['\"].*__import__\(['\"]shutil['\"].*\.rmtree",
        "Python one-liner using __import__ with recursive deletion detected",
    ),
    (
        r"python[23]?\s+-c\s+['\"].*__import__\(['\"]pathlib['\"]",
        "Python one-liner using __import__ with pathlib detected",
    ),
    (
        r"python[23]?\s+-c\s+['\"].*__import__\(['\"]subprocess['\"]",
        "Python one-liner using __import__ with subprocess detected",
    ),
    (
        r"python[23]?\s+-c\s+['\"].*\bexec\s*\(",
        "Python one-liner with exec() detected (potential obfuscation)",
    ),
    (
        r"python[23]?\s+-c\s+['\"].*\beval\s*\(",
        "Python one-liner with eval() detected (potential obfuscation)",
    ),
    (
        r"python[23]?\s+-c\s+['\"].*subprocess\.",
        "Python one-liner with subprocess module detected",
    ),
    (
        r"python[23]?\s+-c\s+['\"].*(decode\(['\"]base64|b64decode|fromhex)",
        "Python one-liner with encoding/decoding detected (potential obfuscation)",
    ),
    # ==========================================================================
    # Perl/Ruby one-liners
    # ==========================================================================
    (
        r"perl\s+-e\s+['\"].*unlink",
        "Perl one-liner with file deletion detected",
    ),
    (
        r"ruby\s+-e\s+['\"].*File(Utils)?\.rm",
        "Ruby one-liner with file deletion detected",
    ),
    # ==========================================================================
    # Command execution bypass (destructive commands hidden in bash -c)
    # ==========================================================================
    (
        r"(ba)?sh\s+-c\s+['\"].*git\s+reset\s+--hard",
        "bash -c with destructive git command detected",
    ),
    (
        r"(ba)?sh\s+-c\s+['\"].*git\s+push\s+.*--force",
        "bash -c with destructive git command detected",
    ),
    (r"(ba)?sh\s+-c\s+['\"].*rm\s+-rf", "bash -c with rm -rf detected"),
    (r"(ba)?sh\s+-c\s+['\"].*shred\b", "bash -c with shred detected"),
    (r"(ba)?sh\s+-c\s+['\"].*dd\s+.*of=", "bash -c with dd detected"),
    (
        r"(ba)?sh\s+-c\s+['\"].*?mv\s+.*?/dev/null\b",
        "bash -c with mv to /dev/null detected",
    ),
    # ==========================================================================
    # eval bypass for destructive commands
    # ==========================================================================
    (r"\beval\s+['\"].*rm\s+-rf", "eval with rm -rf detected"),
    (r"\beval\s+['\"].*shred\b", "eval with shred detected"),
    (r"\beval\s+['\"].*dd\s+.*of=", "eval with dd detected"),
]

# Check if command matches any safe pattern
safe_match = any(re.search(pattern, command) for pattern in SAFE_PATTERNS)

# Check all blocked patterns
for pattern, reason in BLOCKED_PATTERNS:
    if re.search(pattern, command):
        # If the ENTIRE command is just a safe operation, allow it
        # But if there are chained dangerous commands, block
        if safe_match and not any(sep in command for sep in ["&&", "||", ";", "|"]):
            # Safe pattern matched and no command chaining - this is a safe variant
            continue
        c.output.exit_block(
            f"BLOCKED: {reason}\n"
            f"Command: {command}\n"
            "If this operation is truly needed, ask the user for explicit permission."
        )

c.output.exit_success()
