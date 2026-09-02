"""
Extension → category mapping, kept separate from the core logic so it's
easy to see and extend without touching how files actually get moved.
"""

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic", ".tiff"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt", ".pages"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods", ".numbers"},
    "Presentations": {".ppt", ".pptx", ".key", ".odp"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg"},
    "Video": {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".html", ".css", ".json", ".sh", ".jsx", ".tsx"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".deb", ".apk"},
}

FALLBACK_CATEGORY = "Other"


def category_for(extension: str) -> str:
    """Return the category name for a lowercase file extension (with the dot)."""
    ext = extension.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return FALLBACK_CATEGORY
