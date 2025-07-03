#!/usr/bin/env python3

import os
import sys
from pathlib import Path

def update_toc(claude_file):
    """Update TOC for a single CLAUDE.md file"""
    claude_path = Path(claude_file)
    directory = claude_path.parent
    
    print(f"Updating TOC for: {claude_file}")
    
    # Find all .md files except CLAUDE.md in the same directory
    md_files = [f for f in directory.glob("*.md") if f.name != "CLAUDE.md"]
    md_files.sort()
    
    if not md_files:
        print("  No additional .md files found, skipping TOC")
        return
    
    # Generate TOC entries with both Claude @ syntax and Obsidian-style links
    toc_entries = [f"- @{f.name} ([[{f.stem}]])" for f in md_files]
    toc_content = "\n".join(toc_entries)
    
    # Read current content
    with open(claude_path, 'r') as f:
        lines = f.readlines()
    
    # Find TOC block, note block, or insert location
    new_lines = []
    toc_found = False
    inside_toc_block = False
    inside_note_block = False
    note_block_lines = []
    
    for i, line in enumerate(lines):
        if "<!-- TOC-START -->" in line:
            # Start of TOC block - replace entire block
            toc_found = True
            inside_toc_block = True
            new_lines.append("<!-- TOC-START -->\n")
            new_lines.append("## Table of Contents\n")
            new_lines.append(toc_content + "\n")
            new_lines.append("<!-- TOC-END -->\n\n")
            continue
            
        if "<!-- TOC-END -->" in line:
            # End of TOC block - skip this line since we already added it
            inside_toc_block = False
            continue
            
        if inside_toc_block:
            # Skip all lines inside the TOC block
            continue
            
        # Detect note block for TOC
        if line.startswith("> [!NOTE]") and "Table of Contents" in line:
            inside_note_block = True
            note_block_lines = [line]
            continue
            
        if inside_note_block:
            if line.startswith("> ") or line.strip() == "":
                note_block_lines.append(line)
                # Check if this is the end of the note block
                if i + 1 < len(lines) and not lines[i + 1].startswith("> ") and lines[i + 1].strip() != "":
                    # End of note block - insert TOC content
                    toc_found = True
                    inside_note_block = False
                    # Add note block header
                    new_lines.extend(note_block_lines[:-1])  # All but last empty line
                    # Add TOC content as quoted lines
                    for toc_line in toc_content.split('\n'):
                        if toc_line.strip():
                            new_lines.append(f"> {toc_line}\n")
                    new_lines.append(">\n")  # Final empty quote line
                    new_lines.append("\n")   # Blank line after note block
                    note_block_lines = []
                continue
            else:
                # End of note block reached
                toc_found = True
                inside_note_block = False
                # Add note block header
                new_lines.extend(note_block_lines)
                # Add TOC content as quoted lines
                for toc_line in toc_content.split('\n'):
                    if toc_line.strip():
                        new_lines.append(f"> {toc_line}\n")
                new_lines.append(">\n")  # Final empty quote line
                new_lines.append("\n")   # Blank line after note block
                new_lines.append(line)   # Current line
                note_block_lines = []
                continue
            
        if not toc_found and line.startswith("## ") and i > 0:  # First section after title
            # Insert TOC before first section
            new_lines.append("<!-- TOC-START -->\n")
            new_lines.append("## Table of Contents\n")
            new_lines.append(toc_content + "\n")
            new_lines.append("<!-- TOC-END -->\n\n")
            new_lines.append(line)
            toc_found = True
        else:
            new_lines.append(line)
    
    # Write back to file
    with open(claude_path, 'w') as f:
        f.writelines(new_lines)
    
    print("  TOC updated successfully")

def main():
    """Main function to update all CLAUDE.md files in best-practices"""
    print("Searching for CLAUDE.md files in best-practices directories...")
    
    best_practices = Path("docs/best-practices")
    
    if not best_practices.exists():
        print("No best-practices directory found in current path")
        sys.exit(1)
    
    # Find all CLAUDE.md files in subdirectories
    for subdir in best_practices.iterdir():
        if subdir.is_dir():
            claude_file = subdir / "CLAUDE.md"
            if claude_file.exists():
                update_toc(claude_file)
    
    print("TOC update complete!")

if __name__ == "__main__":
    main()