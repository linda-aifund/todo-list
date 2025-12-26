"""
Reusable UI components for the Enhanced Todo App
"""

import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime
from constants import PRIORITIES, FILE_ICONS
from db_helpers import format_time_spent, format_file_size, get_due_date_status


def render_priority_badge(priority: str) -> str:
    """
    Render a priority badge

    Args:
        priority: Priority level ('low', 'medium', 'high')

    Returns:
        HTML string for badge
    """
    if priority not in PRIORITIES:
        priority = 'medium'

    config = PRIORITIES[priority]
    return config['label']


def render_category_chip(category: Optional[Dict]) -> str:
    """
    Render a category chip

    Args:
        category: Category dict with name and color

    Returns:
        HTML/markdown string for category
    """
    if not category:
        return ""

    color = category.get('color', '#6366F1')
    name = category.get('name', 'No Category')

    # Return styled markdown
    return f"🏷️ **{name}**"


def render_tag_chips(tags: List[Dict]) -> str:
    """
    Render tag chips

    Args:
        tags: List of tag dicts

    Returns:
        String with all tags
    """
    if not tags:
        return ""

    tag_names = [f"`{tag['name']}`" for tag in tags]
    return "🔖 " + " ".join(tag_names)


def render_due_date(due_date: Optional[str], completed: bool = False) -> str:
    """
    Render due date with status indicator

    Args:
        due_date: ISO format datetime string
        completed: Whether todo is completed

    Returns:
        Formatted due date string
    """
    if not due_date:
        return ""

    try:
        due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        formatted_date = due.strftime('%b %d, %Y')

        if completed:
            return f"📅 {formatted_date}"

        status = get_due_date_status(due_date)
        return f"{status} 📅 {formatted_date}"

    except:
        return f"📅 {due_date}"


def render_time_tracking(minutes: int) -> str:
    """
    Render time tracking display

    Args:
        minutes: Time spent in minutes

    Returns:
        Formatted time string
    """
    if minutes == 0:
        return "⏱️ No time tracked"

    return f"⏱️ {format_time_spent(minutes)}"


def render_subtask_progress(stats: Dict) -> str:
    """
    Render subtask completion progress

    Args:
        stats: Dict with total, completed, percentage

    Returns:
        Progress string
    """
    if stats['total'] == 0:
        return ""

    return f"✓ {stats['completed']}/{stats['total']} subtasks ({stats['percentage']}%)"


def render_attachment_item(attachment: Dict) -> str:
    """
    Render a single attachment item

    Args:
        attachment: Attachment dict with file_name, file_size

    Returns:
        Formatted attachment string
    """
    icon = get_file_icon(attachment['file_name'])
    size = format_file_size(attachment.get('file_size', 0))

    return f"{icon} {attachment['file_name']} ({size})"


def get_file_icon(file_name: str) -> str:
    """Get icon for file based on extension"""
    extension = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
    return FILE_ICONS.get(extension, FILE_ICONS['default'])


def render_todo_summary(todo: Dict) -> str:
    """
    Render a one-line summary of a todo

    Args:
        todo: Todo dict

    Returns:
        Summary string with priority, category, due date
    """
    parts = []

    # Priority
    parts.append(render_priority_badge(todo.get('priority', 'medium')))

    # Category
    if todo.get('categories'):
        parts.append(render_category_chip(todo['categories']))

    # Due date
    if todo.get('due_date'):
        parts.append(render_due_date(todo['due_date'], todo.get('completed', False)))

    return " | ".join(parts) if parts else ""


def format_todo_title(task: str, completed: bool) -> str:
    """
    Format todo title with strikethrough if completed

    Args:
        task: Task text
        completed: Whether todo is completed

    Returns:
        Formatted markdown string
    """
    if completed:
        return f"~~{task}~~"
    return task


def get_priority_sort_order(priority: str) -> int:
    """Get sort order for priority"""
    return PRIORITIES.get(priority, PRIORITIES['medium'])['sort_order']


def sort_todos(todos: List[Dict], sort_by: str = 'default') -> List[Dict]:
    """
    Sort todos by various criteria

    Args:
        todos: List of todo dicts
        sort_by: Sort criteria ('default', 'priority', 'due_date', 'created')

    Returns:
        Sorted list of todos
    """
    if sort_by == 'priority':
        return sorted(todos, key=lambda x: (
            x.get('completed', False),
            get_priority_sort_order(x.get('priority', 'medium'))
        ))
    elif sort_by == 'due_date':
        return sorted(todos, key=lambda x: (
            x.get('completed', False),
            x.get('due_date') or '9999-12-31'
        ))
    elif sort_by == 'created':
        return sorted(todos, key=lambda x: x.get('created_at', ''), reverse=True)
    else:  # default
        return sorted(todos, key=lambda x: (
            x.get('completed', False),
            get_priority_sort_order(x.get('priority', 'medium')),
            x.get('due_date') or '9999-12-31'
        ))


def render_empty_state(message: str = "No todos found"):
    """Render empty state message"""
    st.info(f"📭 {message}")


def render_success_message(message: str):
    """Render success toast"""
    st.success(f"✅ {message}")


def render_error_message(message: str):
    """Render error toast"""
    st.error(f"❌ {message}")


def render_warning_message(message: str):
    """Render warning toast"""
    st.warning(f"⚠️ {message}")
