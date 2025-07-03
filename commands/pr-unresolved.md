---
name: pr-unresolved
description: List unresolved PR comments
---

```bash
# Get repo and PR from current context or args
if [ -n "$1" ] && [ -n "$2" ]; then
    repo="$1"
    pr="$2"
else
    # Try to detect from current git repo
    repo=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
    pr=$(gh pr view --json number -q .number 2>/dev/null)
fi

if [ -z "$repo" ] || [ -z "$pr" ]; then
    echo "Usage: /pr-unresolved [owner/repo] [PR_NUMBER]"
    echo "Or run from a git repo with an open PR"
    exit 1
fi

source ~/.claude/tools/pr_comments.sh
echo "🔍 Unresolved comments for $repo#$pr:"
get_unresolved_comments_detailed "$repo" "$pr" | awk -F'\t' '{printf "• #%s by @%s: %s\n", $1, $2, $3}'
```