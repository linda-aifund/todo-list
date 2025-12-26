"""
Constants for the Enhanced Todo App
"""

# Priority levels
PRIORITIES = {
    'low': {
        'label': '🟢 Low',
        'color': '#10B981',
        'sort_order': 3
    },
    'medium': {
        'label': '🟡 Medium',
        'color': '#F59E0B',
        'sort_order': 2
    },
    'high': {
        'label': '🔴 High',
        'color': '#EF4444',
        'sort_order': 1
    }
}

PRIORITY_OPTIONS = ['low', 'medium', 'high']

# Status options
STATUS_OPTIONS = {
    'all': 'All Todos',
    'active': 'Active',
    'completed': 'Completed'
}

# File upload settings
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ALLOWED_FILE_TYPES = [
    'pdf', 'doc', 'docx', 'txt', 'md',  # Documents
    'jpg', 'jpeg', 'png', 'gif', 'svg',  # Images
    'zip', 'rar', '7z',  # Archives
    'csv', 'xlsx', 'xls',  # Spreadsheets
    'mp4', 'mov', 'avi',  # Videos
    'mp3', 'wav'  # Audio
]

# File type icons
FILE_ICONS = {
    'pdf': '📄',
    'doc': '📝',
    'docx': '📝',
    'txt': '📝',
    'md': '📝',
    'jpg': '🖼️',
    'jpeg': '🖼️',
    'png': '🖼️',
    'gif': '🖼️',
    'svg': '🖼️',
    'zip': '📦',
    'rar': '📦',
    '7z': '📦',
    'csv': '📊',
    'xlsx': '📊',
    'xls': '📊',
    'mp4': '🎥',
    'mov': '🎥',
    'avi': '🎥',
    'mp3': '🎵',
    'wav': '🎵',
    'default': '📎'
}

# Date format
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

# Time tracking
TIME_INCREMENT_MINUTES = 15  # Default increment for manual time tracking

# UI settings
TODO_EXPANDER_ICON = "📋"
CATEGORY_ICON = "🏷️"
TAG_ICON = "🔖"
DUE_DATE_ICON = "📅"
TIME_ICON = "⏱️"
ATTACHMENT_ICON = "📎"
SUBTASK_ICON = "✓"

# Default category color
DEFAULT_CATEGORY_COLOR = '#6366F1'

# Storage bucket name
STORAGE_BUCKET = 'todo-attachments'
