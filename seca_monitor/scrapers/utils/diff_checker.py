"""
Diff checking utilities for tracking content changes
"""
import hashlib
import difflib
from typing import Tuple


def generate_content_hash(content: str) -> str:
    """
    Generate MD5 hash of content

    Args:
        content: String content to hash

    Returns:
        MD5 hash as hexadecimal string
    """
    if not content:
        return ''
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def compare_content(old_content: str, new_content: str) -> Tuple[bool, str]:
    """
    Compare two content strings and generate diff summary

    Args:
        old_content: Previous content
        new_content: New content

    Returns:
        Tuple of (has_changed: bool, diff_summary: str)
    """
    if not old_content and not new_content:
        return False, ''

    if not old_content:
        return True, 'Initial content added'

    # Generate hashes
    old_hash = generate_content_hash(old_content)
    new_hash = generate_content_hash(new_content)

    # No change if hashes match
    if old_hash == new_hash:
        return False, ''

    # Content changed - generate summary
    diff_summary = generate_diff_summary(old_content, new_content)
    return True, diff_summary


def generate_diff_summary(old_content: str, new_content: str, max_lines: int = 5) -> str:
    """
    Generate a human-readable diff summary

    Args:
        old_content: Previous content
        new_content: New content
        max_lines: Maximum number of diff lines to include

    Returns:
        Diff summary string
    """
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()

    # Use difflib to find differences
    diff = list(difflib.unified_diff(
        old_lines,
        new_lines,
        lineterm='',
        n=0  # Context lines
    ))

    if not diff:
        return 'Content changed (hash mismatch)'

    # Count additions and deletions
    additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))

    summary_parts = []

    if additions > 0:
        summary_parts.append(f"{additions} line(s) added")

    if deletions > 0:
        summary_parts.append(f"{deletions} line(s) removed")

    return ', '.join(summary_parts) if summary_parts else 'Content modified'


def highlight_changes(old_content: str, new_content: str) -> dict:
    """
    Generate detailed change highlighting for display

    Args:
        old_content: Previous content
        new_content: New content

    Returns:
        Dictionary with 'added', 'removed', 'changed' lists
    """
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()

    diff = difflib.unified_diff(old_lines, new_lines, lineterm='', n=0)

    added = []
    removed = []

    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            added.append(line[1:])
        elif line.startswith('-') and not line.startswith('---'):
            removed.append(line[1:])

    return {
        'added': added,
        'removed': removed,
        'has_changes': len(added) > 0 or len(removed) > 0,
    }
