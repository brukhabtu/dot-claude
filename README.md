# Claude Code Settings Repository

This repository contains my personal Claude Code configuration, including settings, custom commands, tools, and coding standards.

## Structure

```
.claude/
├── CLAUDE.md           # Instructions and standards for Claude
├── README.md           # This file - human documentation
├── settings.json       # Claude Code settings
├── commands/           # Custom slash commands
├── tools/              # Custom tools and scripts
└── .gitignore         # Version control exclusions
```

## Documentation Strategy

This repository follows a hybrid documentation approach:

### Local (This Repo)
- **Language best practices** - Universal coding standards that apply everywhere
- **Tool configurations** - Settings and preferences that travel between machines
- **Reusable commands** - Slash commands for common workflows
- **General standards** - Coding principles that apply to all projects

### External (Obsidian Vaults)
- **Project documentation** - Architecture, APIs, component details
- **Context-specific practices** - Work standards vs personal preferences  
- **Session logs** - Daily notes and learning documentation
- **Machine-specific content** - Separate vaults for work/personal computers

## Available Commands

Custom slash commands available in this configuration:

- `/doc-status` - Check documentation coverage for current repository
- `/document-all` - Generate comprehensive documentation using parallel Task agents
- `/journal-entry` - Add session summary to today's daily note
- `/parallel-plan` - Create implementation plans with parallel execution
- `/pr-comment-ids` - Extract comment IDs from GitHub PR discussions
- `/pr-resolve-all` - Resolve all GitHub PR comment discussions
- `/pr-unresolved` - Show unresolved GitHub PR comment discussions
- `/quality` - Run quality checks and analysis
- `/update-toc` - Update table of contents in markdown files
- `/validate-vault` - Validate Obsidian vault structure and links

## Available Tools

Custom tools and scripts in this configuration:

- `check_silent_exceptions.py` - Analyze code for silent exception handling patterns
- `link-to-obsidian.py` - Create symlink between vault and docs folder
- `pr_comments.sh` - Shell script for GitHub PR comment management
- `update-toc.py` - Python script to automatically update table of contents

## Setup

1. Clone this repository to `~/.claude/`
2. Ensure Obsidian vault exists at the configured path
3. Install any required dependencies for custom tools
4. Customize `settings.json` and `CLAUDE.md` as needed

## Maintenance

- **CLAUDE.md**: Update coding standards and workflow instructions
- **Commands**: Add new slash commands in `commands/` directory
- **Tools**: Place custom scripts in `tools/` directory
- **Settings**: Machine-specific preferences in `settings.json`

The goal is to maintain consistency across development environments while keeping project-specific documentation in appropriate external vaults.