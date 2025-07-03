# Claude Code Configuration

## External Documentation
**Obsidian Vault**: `$CLAUDE_VAULT`
See vault's CLAUDE.md for structure guidelines.

## Variables
- `CLAUDE_VAULT="/Users/bruk.habtu/Documents/ObsidianVaults/Claude"` - Obsidian documentation vault path

## Obsidian CLI Integration
The `obs` CLI tool enables querying your Obsidian vault from the command line using Dataview syntax:

**Basic usage:**
```bash
obs query -v $CLAUDE_VAULT "LIST file.name"
obs query -v $CLAUDE_VAULT "TABLE file.name FROM \"Claude-Config\""
obs query -v $CLAUDE_VAULT -f json "LIST WHERE contains(file.path, \"python\")"
```

**Useful queries for Claude documentation:**
```bash
# List all Python best practices
obs query -v $CLAUDE_VAULT "LIST FROM \"Claude-Config/best-practices/python\""

# Recently modified configuration files
obs query -v $CLAUDE_VAULT "TABLE file.name, file.mtime FROM \"Claude-Config\" SORT file.mtime DESC"

# Find specific topics across all best practices
obs query -v $CLAUDE_VAULT "LIST WHERE contains(file.name, \"CONTEXT\")"

# Export results as JSON for processing
obs query -v $CLAUDE_VAULT -f json "TABLE file.name FROM \"Claude-Config\""
```

**Setup:** Run `python3 tools/link-to-obsidian.py` once to create symlink between vault and docs folder.

## Best Practices
Language and technology-specific guidelines:
- `@docs/best-practices/python/CLAUDE.md` - Python coding standards and patterns
- `@docs/best-practices/typescript/CLAUDE.md` - TypeScript types and patterns
- `@docs/best-practices/elixir/CLAUDE.md` - Elixir functional programming patterns

## Workflow
- Always run formatter before code changes
- Run tests after code modifications
- Use $CLAUDE_VAULT variable for vault references
- Check existing documentation before creating new files

## Documentation Strategy
**This repo:** Language standards, tool configs, universal practices
**Obsidian vault:** Project-specific docs, session logs, context-specific practices

## Do Not
- Commit without running linters/formatters
- Hardcode vault paths (use $CLAUDE_VAULT variable)
- Create project documentation that belongs in vault