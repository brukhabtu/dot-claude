---
name: parallel-plan
description: Generate a PLAN.md for parallel agent execution with no conflicts
---

## Your Task: Generate a Parallel Execution Plan

Based on the user's request: **$ARGUMENTS**

Analyze this request and the project structure to create a **PLAN.md** file that:

### 1. **Identifies Independent Work Units**
- Break down the work into modules/components that can be developed independently
- Each unit should have:
  - Clear file boundaries (no two agents touch the same file)
  - Well-defined interfaces
  - Minimal dependencies on other units
  - Specific deliverables

### 2. **Creates Agent Instructions**
Each agent section must include:
```markdown
### Agent N: [Component Name]
**Files to Create/Modify:** (list specific files - ensure NO overlap with other agents)
**Dependencies:** (what this agent needs from other agents, if any)
**Interface:** (what this agent exports/provides)
**Tasks:**
1. Create todos using TodoWrite tool
2. Specific implementation steps
3. Testing requirements
4. Send completion notification
**Deliverables:** (exact files/functions to produce)
**Completion Notification:**
```bash
terminal-notifier -title "Agent N Complete" -message "[Component Name] module finished" -sound Glass
```
```

### 3. **Notification Format Standard**
Each agent MUST send a notification when complete using this format:
```bash
# Success notification
terminal-notifier -title "Agent [N] Complete" -message "[Component Name] module finished successfully" -sound Glass

# Error notification (if applicable)
terminal-notifier -title "Agent [N] Error" -message "[Component Name] failed: [error description]" -sound Basso
```

Notification components:
- **Title**: "Agent [N] [Status]" (e.g., "Agent 3 Complete", "Agent 2 Error")
- **Message**: "[Component Name] [outcome]" (e.g., "Resolver List module finished successfully")
- **Sound**: "Glass" for success, "Basso" for errors
- **Optional**: -group "parallel-plan" to group notifications

### 4. **Emphasizes Parallel Execution**
Include a section like:
```markdown
## CRITICAL: Parallel Execution Instructions

**⚡ MANDATORY: ALL agents MUST be launched in a SINGLE message with multiple Task tool calls**

Example execution:
\```
I'll launch all agents in parallel to implement the plan:

<Task tool calls for Agent 1>
<Task tool calls for Agent 2>
<Task tool calls for Agent 3>
... (all in ONE message)
\```

**❌ DO NOT launch agents sequentially or in separate messages**
**✅ DO launch all agents simultaneously in one message**
```

### 5. **Includes Todo Instructions**
Each agent's instructions MUST include:
```markdown
**First Action: Create Todos**
Use the TodoWrite tool to create a todo list:
- Todo 1: [Specific task]
- Todo 2: [Specific task]
- Mark todos as in_progress when starting
- Mark todos as completed when done
```

### 6. **Defines Success Criteria**
- Clear acceptance criteria for each agent
- Integration points clearly specified
- No merge conflicts possible
- All agents send completion notifications

### 7. **Provides Summary Notification**
After all agents are launched, include a final notification command:
```markdown
## Summary Notification
After launching all agents:
```bash
terminal-notifier -title "Parallel Execution Started" -message "[N] agents working on [project name]" -sound Pop -group "parallel-plan"
```
```

### 8. **Provides Execution Command**
At the end, include:
```markdown
## Execution

To execute this plan, say: "Execute the parallel plan"

Claude will then:
1. Send start notification
2. Launch ALL agents simultaneously (in one message)
3. Each agent will create their own todos
4. Each agent will send completion notification
5. Agents will work independently without conflicts
6. Results will be integrated as specified
```

### Key Principles:
1. **File Ownership**: Each file is owned by exactly ONE agent
2. **Clear Boundaries**: No shared state or files between agents
3. **Interface Contracts**: Define how modules will communicate
4. **Parallel-First Design**: Structure specifically for concurrent execution
5. **Todo Tracking**: Each agent manages their own todo list
6. **Progress Visibility**: Notifications keep user informed of progress

Generate the PLAN.md file with these specifications based on the user's requirements provided in the arguments.