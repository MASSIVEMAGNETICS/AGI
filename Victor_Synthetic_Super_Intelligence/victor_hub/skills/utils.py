"""
Skill Utilities
Shared utility functions for Victor Hub skills
"""


def truncate_string(text: str, max_len: int = 100, ellipsis: str = "...") -> str:
    """
    Truncate a string to a maximum length with optional ellipsis.
    
    Args:
        text: The string to truncate
        max_len: Maximum length of the output string (including ellipsis)
        ellipsis: String to append when truncating (default: "...")
    
    Returns:
        Truncated string with ellipsis if the string was shortened,
        or the original string if it was within max_len
    """
    if len(text) <= max_len:
        return text
    return text[:max_len - len(ellipsis)] + ellipsis


def truncate_preview(text: str, max_len: int = 100) -> str:
    """
    Create a preview of text, truncating if necessary.
    Alias for truncate_string with default parameters.
    """
    return truncate_string(text, max_len)
