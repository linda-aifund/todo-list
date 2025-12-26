"""
Database helper functions for the Enhanced Todo App
"""

from supabase import Client
from typing import List, Dict, Optional, Any
from datetime import datetime


# ============================================================================
# TODOS OPERATIONS
# ============================================================================

def get_all_todos(supabase: Client, filters: Optional[Dict] = None) -> List[Dict]:
    """
    Fetch all todos with optional filters

    Args:
        supabase: Supabase client
        filters: Dict with status, priority, category_id, search_query

    Returns:
        List of todo dictionaries
    """
    query = supabase.table("todos").select("""
        *,
        categories (id, name, color),
        todo_tags (tag_id, tags (id, name))
    """)

    # Apply filters
    if filters:
        if filters.get('status') == 'active':
            query = query.eq('completed', False)
        elif filters.get('status') == 'completed':
            query = query.eq('completed', True)

        if filters.get('priority'):
            query = query.eq('priority', filters['priority'])

        if filters.get('category_id'):
            query = query.eq('category_id', filters['category_id'])

    # Order by priority, then due date, then created date
    response = query.order('completed').order('created_at', desc=True).execute()
    return response.data


def create_todo(supabase: Client, task: str, **kwargs) -> Dict:
    """
    Create a new todo

    Args:
        supabase: Supabase client
        task: Task description
        **kwargs: description, priority, due_date, category_id

    Returns:
        Created todo dict
    """
    todo_data = {
        'task': task,
        'completed': False,
        'description': kwargs.get('description'),
        'priority': kwargs.get('priority', 'medium'),
        'due_date': kwargs.get('due_date'),
        'category_id': kwargs.get('category_id'),
        'time_spent_minutes': 0
    }

    response = supabase.table("todos").insert(todo_data).execute()
    return response.data[0] if response.data else None


def update_todo(supabase: Client, todo_id: int, **kwargs) -> Dict:
    """
    Update a todo

    Args:
        supabase: Supabase client
        todo_id: ID of todo to update
        **kwargs: Fields to update (task, description, priority, due_date, category_id, completed)

    Returns:
        Updated todo dict
    """
    response = supabase.table("todos").update(kwargs).eq('id', todo_id).execute()
    return response.data[0] if response.data else None


def delete_todo(supabase: Client, todo_id: int) -> bool:
    """
    Delete a todo (cascades to subtasks, attachments, todo_tags)

    Args:
        supabase: Supabase client
        todo_id: ID of todo to delete

    Returns:
        True if successful
    """
    response = supabase.table("todos").delete().eq('id', todo_id).execute()
    return True


def update_time_spent(supabase: Client, todo_id: int, additional_minutes: int) -> Dict:
    """
    Add time to a todo's time_spent_minutes

    Args:
        supabase: Supabase client
        todo_id: ID of todo
        additional_minutes: Minutes to add

    Returns:
        Updated todo dict
    """
    # Fetch current time
    todo = supabase.table("todos").select("time_spent_minutes").eq('id', todo_id).execute()
    current_time = todo.data[0]['time_spent_minutes'] if todo.data else 0

    new_time = current_time + additional_minutes
    return update_todo(supabase, todo_id, time_spent_minutes=new_time)


# ============================================================================
# CATEGORIES OPERATIONS
# ============================================================================

def get_all_categories(supabase: Client) -> List[Dict]:
    """Fetch all categories"""
    response = supabase.table("categories").select("*").order('name').execute()
    return response.data


def create_category(supabase: Client, name: str, color: str = '#6366F1') -> Dict:
    """Create a new category"""
    response = supabase.table("categories").insert({'name': name, 'color': color}).execute()
    return response.data[0] if response.data else None


def update_category(supabase: Client, category_id: int, **kwargs) -> Dict:
    """Update a category"""
    response = supabase.table("categories").update(kwargs).eq('id', category_id).execute()
    return response.data[0] if response.data else None


def delete_category(supabase: Client, category_id: int) -> bool:
    """Delete a category (sets todos.category_id to NULL)"""
    response = supabase.table("categories").delete().eq('id', category_id).execute()
    return True


# ============================================================================
# TAGS OPERATIONS
# ============================================================================

def get_all_tags(supabase: Client) -> List[Dict]:
    """Fetch all tags"""
    response = supabase.table("tags").select("*").order('name').execute()
    return response.data


def create_tag(supabase: Client, name: str) -> Dict:
    """Create a new tag"""
    response = supabase.table("tags").insert({'name': name}).execute()
    return response.data[0] if response.data else None


def delete_tag(supabase: Client, tag_id: int) -> bool:
    """Delete a tag (cascades todo_tags)"""
    response = supabase.table("tags").delete().eq('id', tag_id).execute()
    return True


def assign_tags_to_todo(supabase: Client, todo_id: int, tag_ids: List[int]) -> bool:
    """
    Assign tags to a todo (replaces existing tags)

    Args:
        supabase: Supabase client
        todo_id: ID of todo
        tag_ids: List of tag IDs to assign

    Returns:
        True if successful
    """
    # First, remove existing tags
    supabase.table("todo_tags").delete().eq('todo_id', todo_id).execute()

    # Then add new tags
    if tag_ids:
        tag_assignments = [{'todo_id': todo_id, 'tag_id': tag_id} for tag_id in tag_ids]
        supabase.table("todo_tags").insert(tag_assignments).execute()

    return True


def get_todo_tags(supabase: Client, todo_id: int) -> List[Dict]:
    """Get all tags for a specific todo"""
    response = supabase.table("todo_tags").select("tags(*)").eq('todo_id', todo_id).execute()
    return [item['tags'] for item in response.data] if response.data else []


# ============================================================================
# SUBTASKS OPERATIONS
# ============================================================================

def get_subtasks(supabase: Client, todo_id: int) -> List[Dict]:
    """Get all subtasks for a todo, ordered by position"""
    response = supabase.table("subtasks").select("*").eq('todo_id', todo_id).order('position').execute()
    return response.data


def create_subtask(supabase: Client, todo_id: int, title: str, position: Optional[int] = None) -> Dict:
    """Create a new subtask"""
    if position is None:
        # Get max position and add 1
        existing = supabase.table("subtasks").select("position").eq('todo_id', todo_id).order('position', desc=True).limit(1).execute()
        position = (existing.data[0]['position'] + 1) if existing.data else 0

    subtask_data = {
        'todo_id': todo_id,
        'title': title,
        'completed': False,
        'position': position
    }

    response = supabase.table("subtasks").insert(subtask_data).execute()
    return response.data[0] if response.data else None


def update_subtask(supabase: Client, subtask_id: int, **kwargs) -> Dict:
    """Update a subtask"""
    response = supabase.table("subtasks").update(kwargs).eq('id', subtask_id).execute()
    return response.data[0] if response.data else None


def delete_subtask(supabase: Client, subtask_id: int) -> bool:
    """Delete a subtask"""
    response = supabase.table("subtasks").delete().eq('id', subtask_id).execute()
    return True


def get_subtask_completion(supabase: Client, todo_id: int) -> Dict:
    """
    Get subtask completion statistics

    Returns:
        Dict with 'total', 'completed', 'percentage'
    """
    subtasks = get_subtasks(supabase, todo_id)
    total = len(subtasks)
    completed = sum(1 for s in subtasks if s['completed'])
    percentage = (completed / total * 100) if total > 0 else 0

    return {
        'total': total,
        'completed': completed,
        'percentage': round(percentage, 1)
    }


# ============================================================================
# ATTACHMENTS OPERATIONS
# ============================================================================

def get_attachments(supabase: Client, todo_id: int) -> List[Dict]:
    """Get all attachments for a todo"""
    response = supabase.table("attachments").select("*").eq('todo_id', todo_id).order('created_at', desc=True).execute()
    return response.data


def create_attachment(supabase: Client, todo_id: int, file_name: str, file_path: str,
                     file_size: int, mime_type: str) -> Dict:
    """Create an attachment record"""
    attachment_data = {
        'todo_id': todo_id,
        'file_name': file_name,
        'file_path': file_path,
        'file_size': file_size,
        'mime_type': mime_type
    }

    response = supabase.table("attachments").insert(attachment_data).execute()
    return response.data[0] if response.data else None


def delete_attachment(supabase: Client, attachment_id: int) -> bool:
    """Delete an attachment record"""
    response = supabase.table("attachments").delete().eq('id', attachment_id).execute()
    return True


# ============================================================================
# SEARCH AND FILTER HELPERS
# ============================================================================

def search_todos(todos: List[Dict], search_query: str) -> List[Dict]:
    """
    Client-side search across todos

    Args:
        todos: List of todo dicts
        search_query: Search string

    Returns:
        Filtered list of todos
    """
    if not search_query:
        return todos

    search_query = search_query.lower()
    filtered = []

    for todo in todos:
        # Search in task
        if search_query in todo['task'].lower():
            filtered.append(todo)
            continue

        # Search in description
        if todo.get('description') and search_query in todo['description'].lower():
            filtered.append(todo)
            continue

        # Search in tags
        if todo.get('todo_tags'):
            tag_names = [t['tags']['name'].lower() for t in todo['todo_tags'] if t.get('tags')]
            if any(search_query in name for name in tag_names):
                filtered.append(todo)
                continue

    return filtered


def filter_todos_by_tags(todos: List[Dict], tag_ids: List[int]) -> List[Dict]:
    """
    Filter todos that have ANY of the specified tags

    Args:
        todos: List of todo dicts
        tag_ids: List of tag IDs to filter by

    Returns:
        Filtered list of todos
    """
    if not tag_ids:
        return todos

    filtered = []
    for todo in todos:
        if todo.get('todo_tags'):
            todo_tag_ids = [t['tag_id'] for t in todo['todo_tags']]
            if any(tag_id in todo_tag_ids for tag_id in tag_ids):
                filtered.append(todo)

    return filtered


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_time_spent(minutes: int) -> str:
    """
    Format minutes into human-readable string

    Args:
        minutes: Number of minutes

    Returns:
        Formatted string (e.g., "2h 30m" or "45m")
    """
    if minutes < 60:
        return f"{minutes}m"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if remaining_minutes == 0:
        return f"{hours}h"

    return f"{hours}h {remaining_minutes}m"


def format_file_size(bytes: int) -> str:
    """
    Format bytes into human-readable string

    Args:
        bytes: File size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB", "243 KB")
    """
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.1f} KB"
    else:
        return f"{bytes / (1024 * 1024):.1f} MB"


def is_overdue(due_date: Optional[str]) -> bool:
    """Check if a todo is overdue"""
    if not due_date:
        return False

    due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
    return due < datetime.now(due.tzinfo)


def get_due_date_status(due_date: Optional[str]) -> str:
    """
    Get status indicator for due date

    Returns:
        '🔴' for overdue, '🟡' for due soon (within 3 days), '✅' for on track, '' for no due date
    """
    if not due_date:
        return ''

    due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
    now = datetime.now(due.tzinfo)

    if due < now:
        return '🔴'  # Overdue
    elif (due - now).days <= 3:
        return '🟡'  # Due soon
    else:
        return '✅'  # On track
