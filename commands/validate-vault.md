---
name: validate-vault
description: Validate Obsidian vault against tagging and content rules
allowed-tools: [Bash]
---

# Vault Validation

## Running validation checks...

### Vault Detection
```bash
# Try to detect vault from current directory or use CLAUDE_VAULT
if [ -d ".obsidian" ]; then
    vault_path="$(pwd)"
    echo "✓ Using current directory as vault: $vault_path"
elif [ -n "$CLAUDE_VAULT" ] && [ -d "$CLAUDE_VAULT" ]; then
    vault_path="$CLAUDE_VAULT"
    echo "✓ Using CLAUDE_VAULT: $vault_path"
elif [ -n "$OBSIDIAN_VAULT" ] && [ -d "$OBSIDIAN_VAULT" ]; then
    vault_path="$OBSIDIAN_VAULT"
    echo "✓ Using OBSIDIAN_VAULT: $vault_path"
else
    echo "❌ No vault detected. Set CLAUDE_VAULT or run from vault directory."
    exit 1
fi
```

### Validation Results
```bash
# Run obs-cli validation
if command -v obs >/dev/null 2>&1; then
    echo -e "\n📋 Running vault validation...\n"
    obs validate --vault "$vault_path" --verbose $ARGUMENTS
else
    echo "❌ obs-cli not found. Install with: pip install obsidian-dquery"
    exit 1
fi
```

### Quick Stats
```bash
echo -e "\n📊 Vault Statistics:"
# Count files
echo "   Total files: $(find "$vault_path" -name "*.md" -not -path "*/.obsidian/*" | wc -l | tr -d ' ')"

# Count daily notes
daily_count=$(find "$vault_path" -path "*/Daily_Notes/*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "   Daily notes: $daily_count"

# Count unique tags
if command -v obs >/dev/null 2>&1; then
    tag_count=$(obs query --vault "$vault_path" -f json 'TABLE WITHOUT ID tag FROM "" FLATTEN file.tags as tag GROUP BY tag' 2>/dev/null | jq -r '.result.values | length' 2>/dev/null || echo "N/A")
    echo "   Unique tags: $tag_count"
fi
```

## Task
Review the validation results above and help fix any issues found. Common fixes include:
- Adding missing `#daily` tags to daily notes
- Converting tech tags to use `#lang/` prefix (e.g., `#python` → `#lang/python`)
- Reducing tag count on over-tagged files (aim for 3-5 tags)
- Ensuring meeting notes have `#meeting` tag