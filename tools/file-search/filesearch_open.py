#!/usr/bin/env python3
"""
FileSearch Open - Find file and open its folder
Usage: python filesearch_open.py <filename>
"""

import os
import sys
import subprocess
from pathlib import Path

def find_and_open(query, search_dirs=None):
    if search_dirs is None:
        search_dirs = [
            r"C:\Users\Admin\My Drive\LifeWorkspace",
            r"C:\Users\Admin\Projects",
            r"C:\Users\Admin\Desktop",
            r"C:\Users\Admin\Documents",
        ]
    
    print(f"\n  Searching for: {query}\n")
    results = []
    
    for root_dir in search_dirs:
        if not os.path.isdir(root_dir):
            continue
        print(f"  Scanning {root_dir} ...")
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip hidden and system dirs
            dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in ('node_modules', '__pycache__', '.git')]
            
            for f in filenames:
                if query.lower() in f.lower():
                    full_path = os.path.join(dirpath, f)
                    results.append(full_path)
                    print(f"  FOUND: {full_path}")
    
    if not results:
        print("\n  No files found.")
        return
    
    print(f"\n  Found {len(results)} match(es)")
    
    if len(results) == 1:
        folder = os.path.dirname(results[0])
        print(f"  Opening folder: {folder}")
        os.startfile(folder)
    else:
        print("\n  Multiple matches:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r}")
        
        try:
            choice = input("\n  Open which? (number, or Enter to skip): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(results):
                folder = os.path.dirname(results[int(choice) - 1])
                print(f"  Opening: {folder}")
                os.startfile(folder)
        except (ValueError, EOFError):
            pass

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("  Usage: python filesearch_open.py <filename> [directory]")
        print("  Example: python filesearch_open.py TAALLIM_TEACHER_REVIEW_FORM.html")
        print("  Example: python filesearch_open.py .pdf C:\\Users\\Admin\\My Drive\\LifeWorkspace")
        sys.exit(1)
    
    if len(sys.argv) >= 3:
        find_and_open(sys.argv[1], [sys.argv[2]])
    else:
        find_and_open(sys.argv[1])
