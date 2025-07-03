#!/usr/bin/env python3

import os
import sys
from pathlib import Path

def link_to_obsidian():
    """Create symlink from Obsidian vault to Claude docs folder"""
    
    # Get paths
    claude_docs = Path.home() / ".claude" / "docs"
    obsidian_vault = Path.home() / "Documents" / "ObsidianVaults" / "Claude"
    link_target = obsidian_vault / "Claude-Config"
    
    # Verify Claude docs exists
    if not claude_docs.exists():
        print(f"❌ Claude docs folder not found: {claude_docs}")
        sys.exit(1)
    
    # Verify Obsidian vault exists
    if not obsidian_vault.exists():
        print(f"❌ Obsidian vault not found: {obsidian_vault}")
        print("Create the vault first, then run this script.")
        sys.exit(1)
    
    # Check if link already exists
    if link_target.exists():
        if link_target.is_symlink():
            current_target = link_target.resolve()
            if current_target == claude_docs:
                print(f"✅ Symlink already exists and points to correct location")
                print(f"   {link_target} -> {claude_docs}")
                return
            else:
                print(f"⚠️  Symlink exists but points to wrong location:")
                print(f"   Current: {link_target} -> {current_target}")
                print(f"   Expected: {link_target} -> {claude_docs}")
                
                response = input("Remove existing link and create new one? (y/N): ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    sys.exit(1)
                
                link_target.unlink()
        else:
            print(f"❌ Path exists but is not a symlink: {link_target}")
            print("Please remove or rename it manually.")
            sys.exit(1)
    
    # Create the symlink
    try:
        link_target.symlink_to(claude_docs)
        print(f"✅ Created symlink:")
        print(f"   {link_target} -> {claude_docs}")
        print()
        print("You can now access your Claude configuration docs from Obsidian!")
        print("The 'Claude-Config' folder in your vault will show:")
        print("  - best-practices/")
        print("    - python/")
        print("    - typescript/")
        print("    - elixir/")
        print()
        print("Changes made in either location will be reflected in both.")
        
    except OSError as e:
        print(f"❌ Failed to create symlink: {e}")
        sys.exit(1)

if __name__ == "__main__":
    link_to_obsidian()