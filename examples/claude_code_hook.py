#!/usr/bin/env python3
"""Claude Code hook: suggest caching for repeated LLM patterns.

Usage as a post-tool-edit hook in .claude/hooks/post-tool-edit.py:
    python3 examples/claude_code_hook.py "$FILE_PATH"
"""
from __future__ import annotations

import sys

CACHE_PATTERNS = [
    "llm", "chat", "completion", "embedding", "prompt",
    "inference", "generate", "predict", "transform",
]


def main():
    if len(sys.argv) < 2:
        print("Usage: claude_code_hook.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    lower_path = file_path.lower()

    matches = [p for p in CACHE_PATTERNS if p in lower_path]
    if not matches:
        sys.exit(0)

    print(f"[cache-ai] LLM-related file modified: {file_path}")
    print(f"[cache-ai] Matched patterns: {', '.join(matches)}")
    print("[cache-ai] Consider adding caching:")
    print("  from cache_ai import with_prompt_cache, cacheable")
    print('  @with_prompt_cache(provider="anthropic")')
    print("  @cacheable(ttl=300)")


if __name__ == "__main__":
    main()
