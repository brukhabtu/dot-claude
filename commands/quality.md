---
allowed-tools: [Bash]
description: Check code quality using AST analysis for exceptions, types, and formatting
---

# Code Quality Check

## Current Status
!`python3 ~/.claude/tools/check_silent_exceptions.py . --no-snippets | head -10`

!`(uv run mypy . 2>&1 || mypy . 2>&1 || python3 -m mypy . 2>&1) | grep -c "error:" | sed 's/$/ type errors/'`

!`(uv run ruff check . --quiet 2>/dev/null || ruff check . --quiet 2>/dev/null || echo "ruff not available") | wc -l | sed 's/^[[:space:]]*//' | sed 's/$/ formatting issues/'`

## Task
Review the code quality results above and help fix the most critical issues:

1. **Silent exceptions** - Replace bare `except:` with specific exception types
2. **Type errors** - Add missing type annotations  
3. **Formatting** - Fix any critical style issues

Focus on silent exceptions first as they hide real bugs. $ARGUMENTS