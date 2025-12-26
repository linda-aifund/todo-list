import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Import our helper modules
import db_helpers as db
import storage_helpers as storage
import ui_components as ui
from constants import PRIORITY_OPTIONS, STATUS_OPTIONS, TIME_INCREMENT_MINUTES

# Page config
st.set_page_config(
    page_title="Enhanced Todo App",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Initialize Supabase client
@st.cache_resource
def init_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        st.error("Please set SUPABASE_URL and SUPABASE_KEY in your .env file or Streamlit secrets")
        st.stop()

    return create_client(url, key)

supabase = init_supabase()

# Initialize session state
if 'active_timers' not in st.session_state:
    st.session_state.active_timers = {}

if 'timer_start_times' not in st.session_state:
    st.session_state.timer_start_times = {}

if 'editing_todo_id' not in st.session_state:
    st.session_state.editing_todo_id = None

# App title
st.title("📝 Enhanced Todo App")
st.markdown("Powerful task management with categories, tags, subtasks, and file attachments")

# =============================================================================
# SIDEBAR - Filters and Management
# =============================================================================

with st.sidebar:
    st.header("⚙️ Filters & Settings")

    # Search
    search_query = st.text_input("🔍 Search", placeholder="Search todos...")

    # Status filter
    status_filter = st.selectbox(
        "Status",
        options=list(STATUS_OPTIONS.keys()),
        format_func=lambda x: STATUS_OPTIONS[x]
    )

    # Priority filter
    priority_filter = st.selectbox(
        "Priority",
        options=['all'] + PRIORITY_OPTIONS,
        format_func=lambda x: x.title() if x != 'all' else 'All Priorities'
    )

    # Category filter
    categories = db.get_all_categories(supabase)
    category_options = ['all'] + [c['id'] for c in categories]
    category_labels = ['All Categories'] + [c['name'] for c in categories]
    category_filter = st.selectbox(
        "Category",
        options=category_options,
        format_func=lambda x: category_labels[category_options.index(x)]
    )

    # Tags filter
    all_tags = db.get_all_tags(supabase)
    selected_tags = st.multiselect(
        "Tags",
        options=[t['id'] for t in all_tags],
        format_func=lambda x: next((t['name'] for t in all_tags if t['id'] == x), '')
    )

    # Clear filters
    if st.button("🗑️ Clear Filters"):
        st.rerun()

    st.divider()

    # Category Management
    st.subheader("🏷️ Manage Categories")
    with st.expander("Add/Edit Categories"):
        with st.form("add_category_form"):
            new_cat_name = st.text_input("Category Name")
            new_cat_color = st.color_picker("Color", "#6366F1")
            if st.form_submit_button("Add Category"):
                if new_cat_name:
                    try:
                        db.create_category(supabase, new_cat_name, new_cat_color)
                        st.success(f"Added category: {new_cat_name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        # List categories with delete option
        if categories:
            st.write("**Existing Categories:**")
            for cat in categories:
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.markdown(f"🏷️ {cat['name']}")
                with col2:
                    if st.button("❌", key=f"del_cat_{cat['id']}"):
                        try:
                            db.delete_category(supabase, cat['id'])
                            st.success(f"Deleted {cat['name']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    # Tag Management
    st.subheader("🔖 Manage Tags")
    with st.expander("Add/Edit Tags"):
        with st.form("add_tag_form"):
            new_tag_name = st.text_input("Tag Name")
            if st.form_submit_button("Add Tag"):
                if new_tag_name:
                    try:
                        db.create_tag(supabase, new_tag_name)
                        st.success(f"Added tag: {new_tag_name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        # List tags with delete option
        if all_tags:
            st.write("**Existing Tags:**")
            for tag in all_tags:
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.markdown(f"`{tag['name']}`")
                with col2:
                    if st.button("❌", key=f"del_tag_{tag['id']}"):
                        try:
                            db.delete_tag(supabase, tag['id'])
                            st.success(f"Deleted {tag['name']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

# =============================================================================
# MAIN AREA - Add Todo Form
# =============================================================================

st.header("➕ Add New Todo")

with st.expander("Create a new todo", expanded=False):
    with st.form("add_todo_form"):
        col1, col2 = st.columns(2)

        with col1:
            new_task = st.text_input("Task *", placeholder="What needs to be done?")
            new_description = st.text_area("Description", placeholder="Add details...")
            new_priority = st.selectbox("Priority", options=PRIORITY_OPTIONS, index=1)

        with col2:
            new_category = st.selectbox(
                "Category",
                options=[None] + [c['id'] for c in categories],
                format_func=lambda x: "No Category" if x is None else next((c['name'] for c in categories if c['id'] == x), '')
            )
            new_due_date = st.date_input("Due Date", value=None)
            new_tags = st.multiselect(
                "Tags",
                options=[t['id'] for t in all_tags],
                format_func=lambda x: next((t['name'] for t in all_tags if t['id'] == x), '')
            )

        submitted = st.form_submit_button("✅ Add Todo", use_container_width=True)

        if submitted:
            if not new_task:
                st.error("Task cannot be empty!")
            else:
                try:
                    # Create todo
                    todo = db.create_todo(
                        supabase,
                        task=new_task,
                        description=new_description if new_description else None,
                        priority=new_priority,
                        due_date=new_due_date.isoformat() if new_due_date else None,
                        category_id=new_category
                    )

                    # Assign tags if any
                    if new_tags and todo:
                        db.assign_tags_to_todo(supabase, todo['id'], new_tags)

                    st.success(f"✅ Created: {new_task}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating todo: {str(e)}")

# =============================================================================
# MAIN AREA - Display Todos
# =============================================================================

st.header("📋 Your Todos")

# Build filters
filters = {}
if status_filter != 'all':
    filters['status'] = status_filter
if priority_filter != 'all':
    filters['priority'] = priority_filter
if category_filter != 'all':
    filters['category_id'] = category_filter

# Fetch todos
try:
    todos = db.get_all_todos(supabase, filters)

    # Apply client-side search
    if search_query:
        todos = db.search_todos(todos, search_query)

    # Apply tags filter
    if selected_tags:
        todos = db.filter_todos_by_tags(todos, selected_tags)

    # Sort todos
    todos = ui.sort_todos(todos, 'default')

    if not todos:
        ui.render_empty_state("No todos match your filters. Try adjusting your search or filters.")
    else:
        st.write(f"**Showing {len(todos)} todo(s)**")

        for todo in todos:
            # Create expander for each todo
            title = ui.format_todo_title(todo['task'], todo.get('completed', False))
            summary = ui.render_todo_summary(todo)

            # Add due date to title if exists
            due_date_display = ""
            if todo.get('due_date'):
                due_date_display = f" - {ui.render_due_date(todo['due_date'], todo.get('completed', False))}"

            with st.expander(f"{title}{due_date_display} | {summary}" if summary else f"{title}{due_date_display}"):
                # Check if this todo is being edited
                is_editing = st.session_state.editing_todo_id == todo['id']

                if is_editing:
                    # Edit form
                    st.markdown("### ✏️ Edit Todo")
                    with st.form(f"edit_todo_{todo['id']}"):
                        edit_col1, edit_col2 = st.columns(2)

                        with edit_col1:
                            edit_task = st.text_input("Task *", value=todo['task'])
                            edit_description = st.text_area("Description", value=todo.get('description', ''))
                            edit_priority = st.selectbox("Priority", options=PRIORITY_OPTIONS, index=PRIORITY_OPTIONS.index(todo.get('priority', 'medium')))

                        with edit_col2:
                            # Get current category
                            current_category = todo.get('category_id')
                            edit_category = st.selectbox(
                                "Category",
                                options=[None] + [c['id'] for c in categories],
                                index=0 if not current_category else ([None] + [c['id'] for c in categories]).index(current_category),
                                format_func=lambda x: "No Category" if x is None else next((c['name'] for c in categories if c['id'] == x), '')
                            )

                            # Parse current due date
                            current_due = None
                            if todo.get('due_date'):
                                try:
                                    from datetime import datetime
                                    current_due = datetime.fromisoformat(todo['due_date'].replace('Z', '+00:00')).date()
                                except:
                                    pass

                            edit_due_date = st.date_input("Due Date", value=current_due)

                            # Get current tags
                            current_tags = [t['tag_id'] for t in todo.get('todo_tags', [])]
                            edit_tags = st.multiselect(
                                "Tags",
                                options=[t['id'] for t in all_tags],
                                default=current_tags,
                                format_func=lambda x: next((t['name'] for t in all_tags if t['id'] == x), '')
                            )

                        form_col1, form_col2 = st.columns(2)
                        with form_col1:
                            save_button = st.form_submit_button("💾 Save Changes", use_container_width=True)
                        with form_col2:
                            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)

                        if save_button:
                            if not edit_task:
                                st.error("Task cannot be empty!")
                            else:
                                try:
                                    # Update todo
                                    db.update_todo(
                                        supabase,
                                        todo['id'],
                                        task=edit_task,
                                        description=edit_description if edit_description else None,
                                        priority=edit_priority,
                                        due_date=edit_due_date.isoformat() if edit_due_date else None,
                                        category_id=edit_category
                                    )

                                    # Update tags
                                    db.assign_tags_to_todo(supabase, todo['id'], edit_tags)

                                    st.session_state.editing_todo_id = None
                                    st.success("Todo updated!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating todo: {str(e)}")

                        if cancel_button:
                            st.session_state.editing_todo_id = None
                            st.rerun()

                else:
                    # Normal view
                    # Top section: Basic info
                    col1, col2, col3, col4 = st.columns([0.5, 0.3, 0.1, 0.1])

                    with col1:
                        # Checkbox for completion
                        completed = st.checkbox(
                            "Mark as complete",
                            value=todo.get('completed', False),
                            key=f"complete_{todo['id']}"
                        )

                        if completed != todo.get('completed', False):
                            try:
                                db.update_todo(supabase, todo['id'], completed=completed)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating: {str(e)}")

                    with col2:
                        st.markdown(f"**{summary}**")

                    with col3:
                        if st.button("✏️", key=f"edit_{todo['id']}", help="Edit todo"):
                            st.session_state.editing_todo_id = todo['id']
                            st.rerun()

                    with col4:
                        if st.button("🗑️", key=f"del_{todo['id']}", help="Delete todo"):
                            try:
                                # Delete attachments from storage first
                                attachments = db.get_attachments(supabase, todo['id'])
                                for att in attachments:
                                    storage.delete_file(supabase, att['file_path'])

                                # Delete todo (cascades to subtasks, attachments table)
                                db.delete_todo(supabase, todo['id'])
                                st.success("Todo deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting: {str(e)}")

                    st.divider()

                    # Description
                    if todo.get('description'):
                        st.markdown("**Description:**")
                        st.write(todo['description'])
                        st.divider()

                    # Tags
                    if todo.get('todo_tags'):
                        tags = [t['tags'] for t in todo['todo_tags'] if t.get('tags')]
                        if tags:
                            st.markdown(ui.render_tag_chips(tags))
                            st.divider()

                    # Time Tracking
                    st.markdown("**⏱️ Time Tracking:**")
                    time_col1, time_col2, time_col3 = st.columns([0.4, 0.3, 0.3])

                    with time_col1:
                        st.write(ui.render_time_tracking(todo.get('time_spent_minutes', 0)))

                    with time_col2:
                        if st.button("➕ Add 15 min", key=f"time_add_{todo['id']}"):
                            try:
                                db.update_time_spent(supabase, todo['id'], TIME_INCREMENT_MINUTES)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

                    with time_col3:
                        custom_time = st.number_input(
                            "Minutes",
                            min_value=0,
                            step=5,
                            key=f"custom_time_{todo['id']}",
                            label_visibility="collapsed"
                        )
                        if st.button("Add", key=f"time_custom_{todo['id']}"):
                            if custom_time > 0:
                                try:
                                    db.update_time_spent(supabase, todo['id'], custom_time)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")

                    st.divider()

                    # Subtasks
                    st.markdown("**✓ Subtasks:**")

                    subtasks = db.get_subtasks(supabase, todo['id'])
                    subtask_stats = db.get_subtask_completion(supabase, todo['id'])

                    if subtasks:
                        st.write(ui.render_subtask_progress(subtask_stats))

                        for subtask in subtasks:
                            sub_col1, sub_col2 = st.columns([0.9, 0.1])
                            with sub_col1:
                                sub_completed = st.checkbox(
                                    subtask['title'],
                                    value=subtask['completed'],
                                    key=f"subtask_{subtask['id']}"
                                )

                                if sub_completed != subtask['completed']:
                                    try:
                                        db.update_subtask(supabase, subtask['id'], completed=sub_completed)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")

                            with sub_col2:
                                if st.button("🗑️", key=f"del_sub_{subtask['id']}"):
                                    try:
                                        db.delete_subtask(supabase, subtask['id'])
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")

                    # Add new subtask
                    with st.form(f"add_subtask_{todo['id']}"):
                        new_subtask = st.text_input("Add subtask", placeholder="New subtask...", label_visibility="collapsed")
                        if st.form_submit_button("Add Subtask"):
                            if new_subtask:
                                try:
                                    db.create_subtask(supabase, todo['id'], new_subtask)
                                    st.success("Subtask added!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")

                    st.divider()

                    # File Attachments
                    st.markdown("**📎 Attachments:**")

                    attachments = db.get_attachments(supabase, todo['id'])

                    if attachments:
                        for att in attachments:
                            att_col1, att_col2, att_col3 = st.columns([0.6, 0.2, 0.2])

                            with att_col1:
                                st.write(ui.render_attachment_item(att))

                            with att_col2:
                                # Generate signed URL for download
                                success, url, error = storage.get_signed_url(supabase, att['file_path'])
                                if success:
                                    st.markdown(f"[⬇️ Download]({url})")
                                else:
                                    st.error("Can't generate download link")

                            with att_col3:
                                if st.button("🗑️", key=f"del_att_{att['id']}"):
                                    try:
                                        storage.delete_file(supabase, att['file_path'])
                                        db.delete_attachment(supabase, att['id'])
                                        st.success("Attachment deleted!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")

                    # Upload new attachment
                    uploaded_file = st.file_uploader(
                        "Upload file",
                        key=f"upload_{todo['id']}",
                        label_visibility="collapsed"
                    )

                    if uploaded_file:
                        # Validate file
                        is_valid, error_msg = storage.validate_file_upload(uploaded_file, uploaded_file.name)

                        if not is_valid:
                            st.error(error_msg)
                        else:
                            if st.button("📤 Upload File", key=f"upload_btn_{todo['id']}"):
                                with st.spinner("Uploading..."):
                                    try:
                                        success, file_path, error = storage.upload_file(
                                            supabase,
                                            todo['id'],
                                            uploaded_file,
                                            uploaded_file.name
                                        )

                                        if success:
                                            # Save to database
                                            db.create_attachment(
                                                supabase,
                                                todo['id'],
                                                uploaded_file.name,
                                                file_path,
                                                uploaded_file.size,
                                                uploaded_file.type
                                            )
                                            st.success("File uploaded!")
                                            st.rerun()
                                        else:
                                            st.error(f"Upload failed: {error}")

                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")

except Exception as e:
    st.error(f"Error fetching todos: {str(e)}")
    st.info("Make sure you've run the migration.sql file in your Supabase database.")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and Supabase | Enhanced Todo App v2.0")
