---
name: doc-status
description: Check documentation coverage
---

```bash
repo=$(basename $(pwd))
vault="/Users/bruk.habtu/Documents/ObsidianVaults/Claude/Documentation/Repositories/$repo"
[ -d "$vault" ] && echo "📁 Docs: $(find "$vault" -name "*.md" | wc -l)" || echo "📁 No docs yet"

# Detect project type and count modules/packages
if [ -f "package.json" ]; then
    echo "📦 JS/TS packages: $(find . -name "package.json" -not -path "*/node_modules/*" | wc -l)"
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    echo "📦 Python modules: $(find . -name "*.py" -path "*/src/*" -o -name "*.py" -maxdepth 2 | wc -l)"
elif [ -f "Cargo.toml" ]; then
    echo "📦 Rust crates: $(find . -name "Cargo.toml" | wc -l)"
elif [ -f "go.mod" ]; then
    echo "📦 Go modules: $(find . -name "go.mod" | wc -l)"
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    echo "📦 Gradle modules: $(find . -name "build.gradle*" -not -path "*/build/*" | wc -l)"
elif [ -f "pom.xml" ]; then
    echo "📦 Maven modules: $(find . -name "pom.xml" | wc -l)"
else
    echo "📦 Source files: $(find . -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.rs" -o -name "*.go" -o -name "*.java" -o -name "*.c" -o -name "*.cpp" | wc -l)"
fi
```