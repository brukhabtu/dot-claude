---
description: Add an entry to today's daily note based on current session work
---

Create an entry in today's daily note based on what we've been working on in this session.

Use bash commands to get the current date and time (don't rely on environment variables):
!date=$(date +%Y-%m-%d)
!time=$(date +"%H:%M")
!note_path="/Users/bruk.habtu/Documents/ObsidianVaults/Claude/Daily_Notes/$date.md"

@/Users/bruk.habtu/Documents/ObsidianVaults/Claude/Templates/Daily_Note_Template.md

Check if today's daily note exists at $note_path:

**If the file doesn't exist:**
- Create a new daily note using the Daily_Note_Template.md template
- Replace {{date}} with $date, {{time}} with $time
- Replace {{topic}} with a summary of what we've been working on in this session

**If the file already exists:**
- Read the existing daily note content
- Append a new session entry following the existing format pattern
- Use format: `### [time] topic` for the session header
- Add the new session after the existing content (before any final tags)
- Preserve all existing content and formatting

Analyze our current conversation and session to determine:
1. What tasks or problems we've been working on
2. Key discoveries, insights, or learnings from this session
3. Technical details like commands run, files created/modified, or tools used
4. Relevant projects, repositories, or concepts to link to
5. Appropriate tags based on the work done

Create a detailed journal entry summarizing today's session work, including specific accomplishments, technical details, and any notable discoveries or patterns learned.