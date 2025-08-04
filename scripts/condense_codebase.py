#!/usr/bin/env python3
"""
Codebase Condenser Script
Condenses an entire codebase into a single .txt file with tree structure

# Entire codebase
python scripts/condense_codebase.py

# Specific directories/files
python scripts/condense_codebase.py backend/ frontend/ README.md
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import fnmatch
import re

class GitignoreParser:
    """Parse and apply .gitignore patterns"""
    
    # Always ignore these directories
    DEFAULT_IGNORES = [
        '.git',
        '.svn',
        '.hg',
        '.bzr',
        '_darcs',
        'CVS',
        '.DS_Store',
        'Thumbs.db',
        '__pycache__',
        '*.pyc',
        'node_modules',
        '.venv',
        'venv',
        'env',
        '.env.local',
        '.env.*.local',
        'dist',
        'build',
        '.next',
        '.nuxt',
        '.cache',
        '.pytest_cache',
        '.coverage',
        'htmlcov',
        '.tox',
        '.mypy_cache',
        '.ruff_cache',
        '.vscode',
        '.idea',
        '*.egg-info',
        '.eggs',
        'backend/api/rai',  # Ignore RAI directory
        'backend/api/rai/',
        'backend/api/rai/*',
        'frontend/package-lock.json',
        'package-lock.json',
        'docs/',
        'docs'
    ]
    
    def __init__(self, gitignore_path):
        self.patterns = self.DEFAULT_IGNORES.copy()
        self.gitignore_path = Path(gitignore_path)
        self.root_dir = self.gitignore_path.parent
        
        if self.gitignore_path.exists():
            with open(self.gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.patterns.append(line)
    
    def should_ignore(self, path):
        """Check if a path should be ignored based on gitignore patterns"""
        path = Path(path)
        
        # Always ignore .git and other VCS directories
        if path.name in ['.git', '.svn', '.hg', '.bzr', '_darcs', 'CVS']:
            return True
        
        # Check if any parent directory is .git
        for parent in path.parents:
            if parent.name in ['.git', '.svn', '.hg', '.bzr', '_darcs', 'CVS']:
                return True
        
        # Get relative path from root
        try:
            rel_path = path.relative_to(self.root_dir)
            rel_str = str(rel_path).replace('\\', '/')
            
            # Check if this is or is inside backend/api/rai
            if rel_str == 'backend/api/rai' or rel_str.startswith('backend/api/rai/'):
                return True
            
            # Also check individual path components
            parts = rel_str.split('/')
            if len(parts) >= 3 and parts[0] == 'backend' and parts[1] == 'api' and parts[2] == 'rai':
                return True
                
        except ValueError:
            return False
        
        # Convert to string with forward slashes
        rel_str = str(rel_path).replace('\\', '/')
        
        # Check each pattern
        for pattern in self.patterns:
            # Handle directory patterns (ending with /)
            if pattern.endswith('/'):
                pattern_base = pattern.rstrip('/')
                if path.is_dir():
                    if self._match_pattern(rel_str, pattern_base):
                        return True
                # Check if file is within ignored directory
                parts = rel_str.split('/')
                for i in range(len(parts)):
                    partial = '/'.join(parts[:i+1])
                    if self._match_pattern(partial, pattern_base):
                        return True
            else:
                # Regular pattern
                if self._match_pattern(rel_str, pattern):
                    return True
                
                # Check if pattern matches any part of the path
                if '/' not in pattern:
                    # Pattern without slash matches anywhere in tree
                    parts = rel_str.split('/')
                    for part in parts:
                        if self._match_pattern(part, pattern):
                            return True
        
        return False
    
    def _match_pattern(self, path, pattern):
        """Match a path against a gitignore pattern"""
        # Handle negation (patterns starting with !)
        if pattern.startswith('!'):
            return False
        
        # Handle patterns starting with /
        if pattern.startswith('/'):
            pattern = pattern[1:]
            # Must match from root
            return fnmatch.fnmatch(path, pattern)
        
        # Pattern can match anywhere
        if fnmatch.fnmatch(path, pattern):
            return True
        
        # Check if pattern matches end of path
        if path.endswith('/' + pattern) or '/' + pattern + '/' in path:
            return True
            
        return False


def generate_tree(root_path, gitignore_parser, prefix="", is_last=True, max_depth=None, current_depth=0):
    """Generate a tree structure of the directory"""
    lines = []
    root_path = Path(root_path)
    
    # Skip if should be ignored
    if gitignore_parser.should_ignore(root_path):
        return lines
    
    # Add current item
    connector = "└── " if is_last else "├── "
    lines.append(prefix + connector + root_path.name)
    
    # Only recurse if it's a directory and we haven't hit max depth
    if root_path.is_dir() and (max_depth is None or current_depth < max_depth):
        # Get all items and filter
        items = []
        try:
            for item in sorted(root_path.iterdir()):
                if not gitignore_parser.should_ignore(item):
                    items.append(item)
        except PermissionError:
            pass
        
        # Process items
        for i, item in enumerate(items):
            is_last_item = (i == len(items) - 1)
            extension = "    " if is_last else "│   "
            subtree = generate_tree(
                item, 
                gitignore_parser,
                prefix + extension,
                is_last_item,
                max_depth,
                current_depth + 1
            )
            lines.extend(subtree)
    
    return lines


def get_file_content(file_path, root_path):
    """Get the content of a file with proper header"""
    rel_path = Path(file_path).relative_to(root_path)
    content = []
    
    # Add file header
    content.append("=" * 80)
    content.append(f"# FILE: {rel_path}")
    content.append("=" * 80)
    content.append("")
    
    # Try to read file content
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            file_content = f.read()
            content.append(file_content)
    except Exception as e:
        content.append(f"[Error reading file: {e}]")
    
    content.append("")  # Add empty line after file
    return '\n'.join(content)


def process_path(path, root_path, gitignore_parser, processed_files):
    """Process a path (file or directory) and return its contents"""
    path = Path(path)
    contents = []
    
    if path.is_file():
        if not gitignore_parser.should_ignore(path) and path not in processed_files:
            processed_files.add(path)
            contents.append(get_file_content(path, root_path))
    elif path.is_dir():
        # Recursively process directory
        for item in sorted(path.rglob('*')):
            if item.is_file() and not gitignore_parser.should_ignore(item) and item not in processed_files:
                processed_files.add(item)
                contents.append(get_file_content(item, root_path))
    
    return contents


def main():
    parser = argparse.ArgumentParser(description='Condense codebase into a single text file')
    parser.add_argument('paths', nargs='*', help='Specific files or directories to include (default: entire codebase)')
    parser.add_argument('--max-depth', type=int, help='Maximum tree depth to display')
    parser.add_argument('--include-env', action='store_true', help='Include .env files (normally excluded)')
    parser.add_argument('--include-rai', action='store_true', help='Include backend/api/rai directory (normally excluded)')
    args = parser.parse_args()
    
    # Setup paths
    root_path = Path.cwd()
    gitignore_path = root_path / '.gitignore'
    
    # Create gitignore parser
    gitignore_parser = GitignoreParser(gitignore_path)
    
    # Optionally include .env files
    if args.include_env:
        gitignore_parser.patterns = [p for p in gitignore_parser.patterns if not p.startswith('.env')]
    
    # Optionally include RAI directory
    if args.include_rai:
        gitignore_parser.patterns = [p for p in gitignore_parser.patterns 
                                   if p not in ['backend/api/rai', 'backend/api/rai/', 'backend/api/rai/*']]
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path.home() / 'Downloads' / f'codebase_{timestamp}.txt'
    
    print(f"Condensing codebase from: {root_path}")
    print(f"Output file: {output_file}")
    print(f"Ignoring: .git, node_modules, __pycache__, backend/api/rai, and other common directories")
    
    # Prepare output content
    output_lines = []
    
    # Add header
    output_lines.append("=" * 80)
    output_lines.append(f"CODEBASE EXPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append(f"Root Directory: {root_path}")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Generate and add tree structure (always complete)
    output_lines.append("FILE TREE STRUCTURE")
    output_lines.append("-" * 40)
    output_lines.append(str(root_path.name) + "/")
    
    # Generate tree for all subdirectories
    items = []
    try:
        for item in sorted(root_path.iterdir()):
            if not gitignore_parser.should_ignore(item):
                items.append(item)
    except PermissionError:
        pass
    
    for i, item in enumerate(items):
        is_last = (i == len(items) - 1)
        tree_lines = generate_tree(item, gitignore_parser, "", is_last, args.max_depth)
        output_lines.extend(tree_lines)
    
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("FILE CONTENTS")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Process files
    processed_files = set()
    
    if args.paths:
        # Process specific paths provided as arguments
        print(f"Processing specified paths: {args.paths}")
        for path_str in args.paths:
            path = Path(path_str)
            if not path.is_absolute():
                path = root_path / path
            
            if path.exists():
                print(f"  Processing: {path}")
                contents = process_path(path, root_path, gitignore_parser, processed_files)
                output_lines.extend(contents)
            else:
                print(f"  Warning: Path does not exist: {path}")
    else:
        # Process entire codebase (default)
        print("Processing entire codebase (excluding gitignored files)...")
        for item in sorted(root_path.rglob('*')):
            if item.is_file() and not gitignore_parser.should_ignore(item):
                output_lines.append(get_file_content(item, root_path))
                processed_files.add(item)
    
    # Write output file
    output_content = '\n'.join(output_lines)
    
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        # Print summary
        file_count = len(processed_files) if args.paths else output_content.count('# FILE:')
        file_size = output_file.stat().st_size / 1024  # Size in KB
        
        print("")
        print("=" * 50)
        print(f"✓ Successfully created: {output_file}")
        print(f"  Files included: {file_count}")
        print(f"  Output size: {file_size:.2f} KB")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()