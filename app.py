import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
@st.cache_resource
def init_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        st.error("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        st.stop()

    return create_client(url, key)

# Initialize the client
supabase = init_supabase()

# App title
st.title("📝 Simple Todo App with Supabase")
st.markdown("A basic Streamlit app demonstrating Supabase integration")

# Sidebar for connection status
with st.sidebar:
    st.header("⚙️ Configuration")
    st.success("✅ Connected to Supabase")
    st.info("Make sure you have created a 'todos' table in your Supabase database")

    st.markdown("""
    ### Table Schema:
    ```sql
    CREATE TABLE todos (
      id BIGSERIAL PRIMARY KEY,
      task TEXT NOT NULL,
      completed BOOLEAN DEFAULT FALSE,
      created_at TIMESTAMP DEFAULT NOW()
    );
    ```
    """)

# Main app
st.header("Add New Todo")

# Input form
with st.form("add_todo_form"):
    new_task = st.text_input("Enter a new task:")
    submitted = st.form_submit_button("Add Todo")

    if submitted and new_task:
        try:
            data = supabase.table("todos").insert({"task": new_task, "completed": False}).execute()
            st.success(f"✅ Added: {new_task}")
            st.rerun()
        except Exception as e:
            st.error(f"Error adding todo: {str(e)}")

# Display todos
st.header("Your Todos")

try:
    # Fetch all todos
    response = supabase.table("todos").select("*").order("created_at", desc=True).execute()
    todos = response.data

    if not todos:
        st.info("No todos yet! Add one above to get started.")
    else:
        for todo in todos:
            col1, col2, col3 = st.columns([0.1, 0.7, 0.2])

            with col1:
                # Checkbox for completion status
                completed = st.checkbox(
                    "Done",
                    value=todo["completed"],
                    key=f"check_{todo['id']}",
                    label_visibility="collapsed"
                )

                # Update completion status if changed
                if completed != todo["completed"]:
                    try:
                        supabase.table("todos").update({"completed": completed}).eq("id", todo["id"]).execute()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating todo: {str(e)}")

            with col2:
                # Display task with strikethrough if completed
                if todo["completed"]:
                    st.markdown(f"~~{todo['task']}~~")
                else:
                    st.markdown(todo["task"])

            with col3:
                # Delete button
                if st.button("🗑️", key=f"del_{todo['id']}"):
                    try:
                        supabase.table("todos").delete().eq("id", todo["id"]).execute()
                        st.success("Todo deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting todo: {str(e)}")

            st.divider()

except Exception as e:
    st.error(f"Error fetching todos: {str(e)}")
    st.info("Make sure the 'todos' table exists in your Supabase database. See the SQL schema in the sidebar.")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and Supabase")
