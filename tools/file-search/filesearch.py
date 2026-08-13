#!/usr/bin/env python3
"""
FileSearch - Fast Windows File Search Tool
Author: MAHI Kamel Abdelghani
Usage: python filesearch.py [options]
"""

import os
import sys
import time
import argparse
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

VERSION = "1.0.0"


# ─── Formatting ──────────────────────────────────────────────────────────────

def format_size(size_bytes):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def format_time(timestamp):
    """Format timestamp."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


# ─── Search Engine ───────────────────────────────────────────────────────────

class FileSearcher:
    def __init__(self, root=None, max_depth=None, follow_symlinks=False):
        self.root = Path(root) if root else Path.cwd()
        self.max_depth = max_depth
        self.follow_symlinks = follow_symlinks
        self.results = []
        self.scanned = 0
        self.errors = 0

    def _scan(self, path, depth=0):
        """Recursively scan directory."""
        if self.max_depth and depth > self.max_depth:
            return

        try:
            entries = list(os.scandir(path))
        except (PermissionError, OSError):
            self.errors += 1
            return

        for entry in entries:
            self.scanned += 1
            try:
                if entry.is_dir(follow_symlinks=self.follow_symlinks):
                    self._scan(entry.path, depth + 1)
                elif entry.is_file(follow_symlinks=self.follow_symlinks):
                    stat = entry.stat()
                    self.results.append({
                        'path': entry.path,
                        'name': entry.name,
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'created': stat.st_ctime,
                        'ext': os.path.splitext(entry.name)[1].lower(),
                    })
            except (PermissionError, OSError):
                self.errors += 1

    def scan(self):
        """Run full directory scan."""
        self.results = []
        self.scanned = 0
        self.errors = 0
        print(f"  Scanning {self.root} ...")
        start = time.time()
        self._scan(self.root)
        elapsed = time.time() - start
        print(f"  Found {len(self.results)} files ({self.scanned} entries, {self.errors} errors) in {elapsed:.2f}s")
        return self.results

    def search_name(self, query, case_sensitive=False, regex=False):
        """Search by filename pattern."""
        if regex:
            import re
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(query, flags)
            return [r for r in self.results if pattern.search(r['name'])]
        else:
            q = query if case_sensitive else query.lower()
            return [r for r in self.results if q in (r['name'] if case_sensitive else r['name'].lower())]

    def search_ext(self, ext):
        """Search by extension."""
        ext = ext.lower()
        if not ext.startswith('.'):
            ext = '.' + ext
        return [r for r in self.results if r['ext'] == ext]

    def search_size(self, min_size=None, max_size=None):
        """Search by file size."""
        results = self.results
        if min_size is not None:
            results = [r for r in results if r['size'] >= min_size]
        if max_size is not None:
            results = [r for r in results if r['size'] <= max_size]
        return results

    def search_date(self, after=None, before=None):
        """Search by modification date."""
        results = self.results
        if after:
            ts = after.timestamp()
            results = [r for r in results if r['modified'] >= ts]
        if before:
            ts = before.timestamp()
            results = [r for r in results if r['modified'] <= ts]
        return results

    def search_content(self, query, case_sensitive=False, extensions=None):
        """Search file contents (text files only)."""
        results = []
        text_exts = {'.txt', '.md', '.py', '.js', '.ts', '.json', '.xml', '.csv',
                      '.html', '.css', '.yml', '.yaml', '.toml', '.cfg', '.ini',
                      '.bat', '.ps1', '.sh', '.sql', '.java', '.c', '.cpp', '.h',
                      '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt'}
        if extensions:
            text_exts = set(extensions)

        q = query if case_sensitive else query.lower()

        for r in self.results:
            if r['ext'] not in text_exts:
                continue
            if r['size'] > 10 * 1024 * 1024:  # skip files > 10MB for content search
                continue
            try:
                with open(r['path'], 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        check = line if case_sensitive else line.lower()
                        if q in check:
                            results.append({
                                **r,
                                'match_line': i,
                                'match_text': line.strip()[:120],
                            })
                            break
            except (PermissionError, OSError):
                self.errors += 1
        return results

    def find_duplicates(self, by_name=False):
        """Find duplicate files by hash or name."""
        groups = defaultdict(list)
        for r in self.results:
            if by_name:
                groups[r['name'].lower()].append(r)
            else:
                try:
                    h = hashlib.md5(open(r['path'], 'rb').read()).hexdigest()
                    groups[h].append(r)
                except (PermissionError, OSError):
                    self.errors += 1

        dupes = {k: v for k, v in groups.items() if len(v) > 1}
        return dupes

    def recent_files(self, days=7, top=50):
        """Get most recently modified files."""
        cutoff = (datetime.now() - timedelta(days=days)).timestamp()
        recent = [r for r in self.results if r['modified'] >= cutoff]
        recent.sort(key=lambda x: x['modified'], reverse=True)
        return recent[:top]

    def largest_files(self, top=50):
        """Get largest files."""
        sorted_results = sorted(self.results, key=lambda x: x['size'], reverse=True)
        return sorted_results[:top]

    def by_extension_stats(self):
        """Get file count and size by extension."""
        stats = defaultdict(lambda: {'count': 0, 'size': 0})
        for r in self.results:
            ext = r['ext'] or '(no ext)'
            stats[ext]['count'] += 1
            stats[ext]['size'] += r['size']
        return dict(sorted(stats.items(), key=lambda x: x[1]['count'], reverse=True))

    def by_folder_stats(self):
        """Get file count and size by folder."""
        stats = defaultdict(lambda: {'count': 0, 'size': 0})
        for r in self.results:
            folder = os.path.dirname(r['path'])
            stats[folder]['count'] += 1
            stats[folder]['size'] += r['size']
        return dict(sorted(stats.items(), key=lambda x: x[1]['size'], reverse=True)[:30])


# ─── Display ─────────────────────────────────────────────────────────────────

def print_results(results, limit=50, show_path=True):
    """Pretty print search results."""
    if not results:
        print("  No results found.")
        return

    print(f"\n  {'-' * 70}")
    for i, r in enumerate(results[:limit]):
        size = format_size(r['size'])
        date = format_time(r['modified'])
        path = r['path'] if show_path else r['name']
        ext = r['ext'] or '--'

        if 'match_line' in r:
            print(f"  {i+1:4}. [{ext:6}] {size:>10}  {date}  {path}")
            print(f"        Line {r['match_line']}: {r['match_text']}")
        else:
            print(f"  {i+1:4}. [{ext:6}] {size:>10}  {date}  {path}")

    if len(results) > limit:
        print(f"\n  ... and {len(results) - limit} more results")
    print(f"  {'-' * 70}")
    print(f"  Total: {len(results)} files")


def print_stats(title, stats, limit=20):
    """Print extension or folder stats."""
    print(f"\n  {title}")
    print(f"  {'-' * 50}")
    for i, (key, val) in enumerate(list(stats.items())[:limit]):
        size = format_size(val['size'])
        print(f"  {i+1:4}. {key:12} {val['count']:6} files  {size:>10}")
    print(f"  {'-' * 50}")


def print_duplicates(dupes, limit=20):
    """Print duplicate file groups."""
    print(f"\n  Duplicate Files (by hash)")
    print(f"  {'-' * 60}")
    shown = 0
    for h, files in dupes.items():
        if shown >= limit:
            break
        print(f"\n  Hash: {h}")
        total_waste = sum(f['size'] for f in files[1:])
        for f in files:
            print(f"    {format_size(f['size']):>10}  {f['path']}")
        print(f"    WASTE: {format_size(total_waste)}")
        shown += 1
    print(f"  {'-' * 60}")
    total_dupes = sum(len(v) - 1 for v in dupes.values())
    total_wasted = sum(sum(f['size'] for f in v[1:]) for v in dupes.values())
    print(f"  Total: {len(dupes)} groups, {total_dupes} duplicates, {format_size(total_wasted)} wasted")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_size(s):
    """Parse size string like '10MB', '1GB', '500KB'."""
    s = s.strip().upper()
    multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
    for suffix, mult in multipliers.items():
        if s.endswith(suffix):
            return int(float(s[:-len(suffix)]) * mult)
    return int(s)


def parse_date(s):
    """Parse date string."""
    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%d/%m/%Y']:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {s}")


def main():
    parser = argparse.ArgumentParser(
        description="FileSearch - Fast Windows File Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  filesearch.py photos                          # Search by name
  filesearch.py -ext .py -ext .md               # Search by extension
  filesearch.py --size-min 1GB                  # Files larger than 1GB
  filesearch.py --content "TODO"                # Search file contents
  filesearch.py --recent 7                      # Modified in last 7 days
  filesearch.py --dupes                         # Find duplicate files
  filesearch.py --largest                       # Show largest files
  filesearch.py --ext-stats                     # Extension statistics
  filesearch.py --root C:\\Users\\Admin -ext .pdf  # Search specific folder
        """
    )

    parser.add_argument('query', nargs='?', help='Search query (filename pattern)')
    parser.add_argument('--root', '-r', default='.', help='Root directory to search (default: current)')
    parser.add_argument('--ext', '-e', action='append', dest='extensions', help='File extension filter (can repeat)')
    parser.add_argument('--content', '-c', help='Search inside file contents')
    parser.add_argument('--size-min', help='Min file size (e.g. 10MB, 1GB)')
    parser.add_argument('--size-max', help='Max file size')
    parser.add_argument('--after', help='Modified after date (YYYY-MM-DD)')
    parser.add_argument('--before', help='Modified before date')
    parser.add_argument('--recent', type=int, metavar='DAYS', help='Modified in last N days')
    parser.add_argument('--largest', type=int, nargs='?', const=50, help='Show N largest files (default 50)')
    parser.add_argument('--dupes', action='store_true', help='Find duplicate files')
    parser.add_argument('--dupes-name', action='store_true', help='Find duplicates by name only')
    parser.add_argument('--ext-stats', action='store_true', help='Show extension statistics')
    parser.add_argument('--folder-stats', action='store_true', help='Show folder size statistics')
    parser.add_argument('--case', '-i', action='store_true', help='Case-sensitive search')
    parser.add_argument('--regex', action='store_true', help='Use regex for name search')
    parser.add_argument('--depth', type=int, help='Max directory depth')
    parser.add_argument('--limit', '-n', type=int, default=50, help='Max results to show (default 50)')
    parser.add_argument('--version', '-v', action='version', version=f'FileSearch {VERSION}')

    args = parser.parse_args()

    # Parse root
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"  Error: '{root}' is not a directory")
        sys.exit(1)

    print(f"\n  FileSearch {VERSION}")
    print(f"  Root: {root}")

    # Initialize searcher
    searcher = FileSearcher(root=root, max_depth=args.depth)

    # Scan
    start = time.time()
    searcher.scan()

    # Apply filters
    results = searcher.results

    if args.extensions:
        ext_results = []
        for ext in args.extensions:
            ext_results.extend(searcher.search_ext(ext))
        results = ext_results

    if args.size_min:
        min_s = parse_size(args.size_min)
        results = [r for r in results if r['size'] >= min_s]

    if args.size_max:
        max_s = parse_size(args.size_max)
        results = [r for r in results if r['size'] <= max_s]

    if args.after:
        after_dt = parse_date(args.after)
        ts = after_dt.timestamp()
        results = [r for r in results if r['modified'] >= ts]

    if args.before:
        before_dt = parse_date(args.before)
        ts = before_dt.timestamp()
        results = [r for r in results if r['modified'] <= ts]

    if args.recent:
        cutoff = (datetime.now() - timedelta(days=args.recent)).timestamp()
        results = [r for r in results if r['modified'] >= cutoff]
        results.sort(key=lambda x: x['modified'], reverse=True)

    if args.content:
        content_results = searcher.search_content(
            args.content, case_sensitive=args.case, extensions=args.extensions
        )
        results = content_results

    if args.query:
        results = searcher.search_name(args.query, case_sensitive=args.case, regex=args.regex)

    # Special modes
    if args.dupes:
        print(f"\n  Scanning for duplicates (hashing files)...")
        dupes = searcher.find_duplicates()
        print_duplicates(dupes, limit=args.limit)
        return

    if args.dupes_name:
        dupes = searcher.find_duplicates(by_name=True)
        print_duplicates(dupes, limit=args.limit)
        return

    if args.ext_stats:
        stats = searcher.by_extension_stats()
        print_stats("Extension Statistics", stats, limit=args.limit)
        return

    if args.folder_stats:
        stats = searcher.by_folder_stats()
        print_stats("Folder Size Statistics (top 30)", stats, limit=args.limit)
        return

    if args.largest is not None:
        top = searcher.largest_files(top=args.largest)
        print(f"\n  Top {len(top)} Largest Files:")
        print_results(top, limit=args.limit)
        return

    # Default: print results
    print_results(results, limit=args.limit)
    print(f"\n  Scan time: {time.time() - start:.2f}s total")


if __name__ == '__main__':
    main()
