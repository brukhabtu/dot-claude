---
name: document-all
description: Document entire repository with Task agents
---

```bash
repo=$(basename $(pwd))
echo "📚 Documenting: $repo"

# Detect project structure and count modules
if [ -f "package.json" ]; then
    modules=$(find . -name "package.json" -not -path "*/node_modules/*" | wc -l)
    echo "Found $modules JS/TS packages"
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    modules=$(find . -name "*.py" -path "*/src/*" -o -name "*.py" -maxdepth 2 | wc -l)
    echo "Found $modules Python modules"
elif [ -f "Cargo.toml" ]; then
    modules=$(find . -name "Cargo.toml" | wc -l)
    echo "Found $modules Rust crates"
elif [ -f "go.mod" ]; then
    modules=$(find . -name "go.mod" | wc -l)
    echo "Found $modules Go modules"
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    modules=$(find . -name "build.gradle*" -not -path "*/build/*" | wc -l)
    echo "Found $modules Gradle modules"
elif [ -f "pom.xml" ]; then
    modules=$(find . -name "pom.xml" | wc -l)
    echo "Found $modules Maven modules"
else
    modules=$(find . -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.rs" -o -name "*.go" -o -name "*.java" -o -name "*.c" -o -name "*.cpp" | wc -l)
    echo "Found $modules source files"
fi
```

Analyze the project structure and create comprehensive documentation by intelligently distributing the work across multiple Task agents.

**Documentation Strategy:**
1. **Analyze the codebase** to identify logical components (modules, features, integrations, etc.)
2. **Create as many Task agents as needed** - one per major component, folder, or logical grouping
3. **CRITICAL: Launch ALL agents in PARALLEL** - Use a single message with multiple concurrent Task tool calls
4. **DO NOT run agents sequentially** - All Task agents must execute simultaneously for maximum efficiency
5. **Each agent should focus** on documenting a specific, well-defined area

**Agent Assignment Examples:**
- Core architecture and main modules
- Individual feature modules or packages
- Integration components (APIs, third-party services)
- Infrastructure (build, CI/CD, configuration)
- Testing and development tools

**Documentation Standards:**
- Create structured markdown files with clear sections
- Include code examples and implementation details
- Document integration points and dependencies
- Follow consistent naming and organization patterns
- Cross-reference related components

**EXECUTION REQUIREMENT:**
**MUST use parallel execution** - Send ONE message containing ALL Task tool calls simultaneously. Do NOT send multiple messages or run agents one after another.

Each agent should create detailed, focused documentation for their assigned area.
Output: /Users/bruk.habtu/Documents/ObsidianVaults/Claude/Documentation/Repositories/{{repo}}/