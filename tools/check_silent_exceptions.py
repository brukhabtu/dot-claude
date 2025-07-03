#!/usr/bin/env python3
"""Tool to detect silent exception handling patterns using AST analysis.

This tool identifies potentially problematic exception handling patterns:
- Bare except clauses
- Empty except blocks  
- Generic Exception catches with pass
- Missing logging in exception handlers
"""

import ast
import argparse
import sys
from pathlib import Path
from typing import List, NamedTuple, Optional


class SilentExceptionIssue(NamedTuple):
    """Represents a silent exception handling issue."""
    file_path: str
    line_number: int
    column: int
    issue_type: str
    description: str
    code_snippet: Optional[str] = None


class SilentExceptionVisitor(ast.NodeVisitor):
    """AST visitor to detect silent exception handling patterns."""
    
    def __init__(self, file_path: str, source_lines: List[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.issues: List[SilentExceptionIssue] = []
    
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Visit exception handler nodes."""
        line_num = node.lineno
        col = getattr(node, 'col_offset', 0)
        
        # Check for bare except
        if node.type is None:
            self.issues.append(SilentExceptionIssue(
                file_path=self.file_path,
                line_number=line_num,
                column=col,
                issue_type="bare_except",
                description="Bare 'except:' clause catches all exceptions",
                code_snippet=self._get_code_snippet(line_num)
            ))
        
        # Check for overly broad Exception catches
        elif (isinstance(node.type, ast.Name) and 
              node.type.id in ['Exception', 'BaseException']):
            if self._is_silent_handler(node):
                self.issues.append(SilentExceptionIssue(
                    file_path=self.file_path,
                    line_number=line_num,
                    column=col,
                    issue_type="broad_exception",
                    description=f"Broad '{node.type.id}' catch with silent handling",
                    code_snippet=self._get_code_snippet(line_num)
                ))
        
        # Check for empty except blocks
        if self._is_empty_handler(node):
            self.issues.append(SilentExceptionIssue(
                file_path=self.file_path,
                line_number=line_num,
                column=col,
                issue_type="empty_except",
                description="Empty except block - exceptions are silently ignored",
                code_snippet=self._get_code_snippet(line_num)
            ))
        
        # Check for pass-only handlers
        elif self._is_pass_only_handler(node):
            self.issues.append(SilentExceptionIssue(
                file_path=self.file_path,
                line_number=line_num,
                column=col,
                issue_type="pass_only",
                description="Exception handler only contains 'pass' statement",
                code_snippet=self._get_code_snippet(line_num)
            ))
        
        self.generic_visit(node)
    
    def _is_silent_handler(self, node: ast.ExceptHandler) -> bool:
        """Check if exception handler silently ignores exceptions."""
        return (self._is_empty_handler(node) or 
                self._is_pass_only_handler(node) or
                not self._has_logging_or_reraise(node))
    
    def _is_empty_handler(self, node: ast.ExceptHandler) -> bool:
        """Check if except block is completely empty."""
        return len(node.body) == 0
    
    def _is_pass_only_handler(self, node: ast.ExceptHandler) -> bool:
        """Check if except block only contains pass statement."""
        return (len(node.body) == 1 and 
                isinstance(node.body[0], ast.Pass))
    
    def _has_logging_or_reraise(self, node: ast.ExceptHandler) -> bool:
        """Check if handler has logging, print, or reraise statements."""
        for stmt in ast.walk(node):
            # Check for logging calls
            if (isinstance(stmt, ast.Call) and 
                isinstance(stmt.func, ast.Attribute) and
                stmt.func.attr in ['debug', 'info', 'warning', 'error', 'critical', 'exception']):
                return True
            
            # Check for print calls
            if (isinstance(stmt, ast.Call) and 
                isinstance(stmt.func, ast.Name) and
                stmt.func.id == 'print'):
                return True
            
            # Check for raise statements (reraise)
            if isinstance(stmt, ast.Raise):
                return True
            
            # Check for return statements (might be intentional handling)
            if isinstance(stmt, ast.Return):
                return True
                
        return False
    
    def _get_code_snippet(self, line_num: int, context_lines: int = 2) -> str:
        """Get code snippet around the given line number."""
        start = max(0, line_num - context_lines - 1)
        end = min(len(self.source_lines), line_num + context_lines)
        
        lines = []
        for i in range(start, end):
            marker = ">>> " if i == line_num - 1 else "    "
            lines.append(f"{marker}{i+1:3d}: {self.source_lines[i].rstrip()}")
        
        return "\n".join(lines)


def analyze_file(file_path: Path) -> List[SilentExceptionIssue]:
    """Analyze a single Python file for silent exception handling."""
    try:
        source_code = file_path.read_text(encoding='utf-8')
        source_lines = source_code.splitlines()
        
        # Parse the AST
        tree = ast.parse(source_code, filename=str(file_path))
        
        # Visit nodes to find issues
        visitor = SilentExceptionVisitor(str(file_path), source_lines)
        visitor.visit(tree)
        
        return visitor.issues
        
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}", file=sys.stderr)
        return []


def analyze_directory(directory: Path, exclude_patterns: List[str] = None) -> List[SilentExceptionIssue]:
    """Analyze all Python files in a directory."""
    if exclude_patterns is None:
        exclude_patterns = ['__pycache__', '.git', '.venv', 'node_modules', 'temp_ask_claude']
    
    all_issues = []
    
    for py_file in directory.rglob('*.py'):
        # Skip excluded directories
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue
            
        issues = analyze_file(py_file)
        all_issues.extend(issues)
    
    return all_issues


def format_issue_report(issues: List[SilentExceptionIssue], show_snippets: bool = True) -> str:
    """Format issues into a readable report."""
    if not issues:
        return "✅ No silent exception handling issues found!"
    
    report = []
    report.append(f"🚨 Found {len(issues)} silent exception handling issues:\n")
    
    # Group by file
    by_file = {}
    for issue in issues:
        if issue.file_path not in by_file:
            by_file[issue.file_path] = []
        by_file[issue.file_path].append(issue)
    
    for file_path, file_issues in sorted(by_file.items()):
        report.append(f"📁 {file_path}")
        report.append("=" * len(file_path))
        
        for issue in sorted(file_issues, key=lambda x: x.line_number):
            report.append(f"  Line {issue.line_number}: {issue.description} [{issue.issue_type}]")
            
            if show_snippets and issue.code_snippet:
                report.append("  Code:")
                for line in issue.code_snippet.split('\n'):
                    report.append(f"    {line}")
            
            report.append("")
        
        report.append("")
    
    # Summary by issue type
    issue_counts = {}
    for issue in issues:
        issue_counts[issue.issue_type] = issue_counts.get(issue.issue_type, 0) + 1
    
    report.append("📊 Issue Summary:")
    for issue_type, count in sorted(issue_counts.items()):
        report.append(f"  {issue_type}: {count}")
    
    return "\n".join(report)


def get_files_with_issues(issues: List[SilentExceptionIssue]) -> List[str]:
    """Get unique list of files that have issues."""
    files = set()
    for issue in issues:
        files.add(issue.file_path)
    return sorted(list(files))


def main():
    """Main entry point for the tool."""
    parser = argparse.ArgumentParser(
        description="Detect silent exception handling patterns in Python code"
    )
    parser.add_argument(
        "path",
        type=Path,
        help="File or directory to analyze"
    )
    parser.add_argument(
        "--no-snippets",
        action="store_true",
        help="Don't show code snippets in output"
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Patterns to exclude from analysis (can be used multiple times)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--files-only",
        action="store_true",
        help="Output only the list of files with issues (one per line)"
    )
    parser.add_argument(
        "--parallel-fix",
        action="store_true",
        help="Output parallel fix plan for files with issues"
    )
    
    args = parser.parse_args()
    
    if not args.path.exists():
        print(f"Error: Path {args.path} does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Analyze files
    if args.path.is_file():
        issues = analyze_file(args.path)
    else:
        exclude_patterns = ['__pycache__', '.git', '.venv', 'node_modules', 'temp_ask_claude']
        exclude_patterns.extend(args.exclude)
        issues = analyze_directory(args.path, exclude_patterns)
    
    # Handle different output modes
    if args.files_only:
        files_with_issues = get_files_with_issues(issues)
        for file_path in files_with_issues:
            print(file_path)
        sys.exit(len(issues))
    
    if args.parallel_fix:
        files_with_issues = get_files_with_issues(issues)
        print(f"Found {len(issues)} issues in {len(files_with_issues)} files:")
        for file_path in files_with_issues:
            print(f"  {file_path}")
        
        if len(files_with_issues) > 5:
            print(f"\n🚀 Parallel fix recommended for {len(files_with_issues)} files")
            print("Execute with parallel agents for faster fixing")
        elif len(files_with_issues) > 0:
            print(f"\n✅ Sequential fix recommended for {len(files_with_issues)} files")
            print("Small number of files can be fixed sequentially")
        else:
            print("\n✅ No files need fixing!")
        
        sys.exit(len(issues))
    
    # Output results
    if args.json:
        import json
        files_with_issues = get_files_with_issues(issues)
        result = {
            "issues": [issue._asdict() for issue in issues],
            "total_count": len(issues),
            "files_with_issues": files_with_issues,
            "files_count": len(files_with_issues),
            "summary": {}
        }
        for issue in issues:
            issue_type = issue.issue_type
            result["summary"][issue_type] = result["summary"].get(issue_type, 0) + 1
        
        print(json.dumps(result, indent=2))
    else:
        report = format_issue_report(issues, show_snippets=not args.no_snippets)
        print(report)
    
    # Exit with error code if issues found
    sys.exit(len(issues))


if __name__ == "__main__":
    main()