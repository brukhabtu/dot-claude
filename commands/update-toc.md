---
name: update-toc
description: Update table of contents in best-practices CLAUDE.md files
---

Update the table of contents for all CLAUDE.md files in the best-practices directories.

This command runs the Python script that:
- Finds all CLAUDE.md files in docs/best-practices subdirectories
- Generates TOCs based on sibling .md files in each directory
- Updates the files with current TOC information
- Skips directories with no additional .md files

```bash
cd ~/.claude && python3 tools/update-toc.py
```

The script automatically handles:
- Creating TOC sections if they don't exist
- Updating existing TOC sections with current files
- Using the `@` import syntax for Claude-friendly references
- Preserving all other file content