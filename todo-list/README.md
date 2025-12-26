# Enhanced Todo App with Streamlit and Supabase

A feature-rich task management application built with Streamlit and Supabase, offering comprehensive todo tracking with priorities, categories, tags, subtasks, file attachments, and time tracking.

## ✨ Features

### Core Features
- ✅ **Create, Read, Update, Delete** todos
- 🎯 **Priority Levels** - High, Medium, Low with visual indicators
- 🏷️ **Categories** - Organize todos with custom categories and colors
- 🔖 **Tags** - Add multiple tags to todos for flexible organization
- 📅 **Due Dates** - Set deadlines with overdue indicators
- 📝 **Notes/Descriptions** - Add detailed descriptions to todos
- ⏱️ **Time Tracking** - Track time spent on each task
- ✓ **Subtasks** - Break down todos into smaller tasks with progress tracking
- 📎 **File Attachments** - Upload and manage files with Supabase Storage

### Search & Filter
- 🔍 **Full-Text Search** - Search across tasks, descriptions, and tags
- 🎚️ **Advanced Filters** - Filter by status, priority, category, and tags
- 📊 **Smart Sorting** - Automatic sorting by priority and due date

### User Experience
- 🎨 **Clean, Intuitive UI** - Modern interface with expandable todo cards
- 🚀 **Real-Time Updates** - Instant sync with Supabase
- 📱 **Responsive Design** - Works on desktop and mobile
- 🎭 **Visual Indicators** - Color-coded priorities and due date status

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- A Supabase account ([Sign up here](https://supabase.com))
- Git (for deployment)

### Installation

1. **Navigate to the project directory**
   ```bash
   cd /home/linda/projects
   ```

2. **Activate the virtual environment**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies** (if not already installed)
   ```bash
   pip install -r requirements.txt
   ```

### Database Setup

1. **Create Supabase Project**
   - Go to [Supabase](https://app.supabase.com)
   - Create a new project
   - Wait for the project to be ready

2. **Run Database Migration**
   - Go to the SQL Editor in your Supabase dashboard
   - Copy and paste the contents of `migration.sql`
   - Execute the SQL script

3. **Create Storage Bucket**
   - Go to Storage in your Supabase dashboard
   - Create a new bucket named `todo-attachments`
   - Set it to **Private**
   - Configure RLS (Row Level Security) policies:
     ```sql
     -- Allow authenticated users
     CREATE POLICY "Allow all operations for authenticated users"
     ON storage.objects FOR ALL
     TO authenticated
     USING (bucket_id = 'todo-attachments');
     ```

4. **Get API Credentials**
   - Go to **Project Settings** > **API**
   - Copy your **Project URL**
   - Copy your **anon/public key**

### Configuration

1. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your Supabase credentials**
   ```bash
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

### Running Locally

```bash
cd /home/linda/projects
source venv/bin/activate
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📖 Usage Guide

### Creating a Todo

1. Click **"Create a new todo"** expander
2. Fill in the task details:
   - **Task** (required) - What needs to be done
   - **Description** - Additional details
   - **Priority** - High, Medium, or Low
   - **Category** - Select from your categories
   - **Due Date** - Set a deadline
   - **Tags** - Add relevant tags
3. Click **"Add Todo"**

### Managing Categories

1. Go to sidebar > **"Manage Categories"**
2. Click **"Add/Edit Categories"**
3. Enter category name and choose a color
4. Click **"Add Category"**
5. Delete categories using the ❌ button

### Managing Tags

1. Go to sidebar > **"Manage Tags"**
2. Click **"Add/Edit Tags"**
3. Enter tag name
4. Click **"Add Tag"**
5. Delete tags using the ❌ button

### Adding Subtasks

1. Expand a todo card
2. Scroll to the **Subtasks** section
3. Enter subtask text
4. Click **"Add Subtask"**
5. Check/uncheck to mark subtasks complete

### Tracking Time

1. Expand a todo card
2. In the **Time Tracking** section:
   - Click **"Add 15 min"** for quick increment
   - Or enter custom minutes and click **"Add"**

### Uploading Files

1. Expand a todo card
2. Scroll to **Attachments** section
3. Click **"Browse files"** or drag and drop
4. Click **"Upload File"**
5. Download files using the ⬇️ link
6. Delete attachments using the 🗑️ button

**Supported File Types:**
- Documents: PDF, DOC, DOCX, TXT, MD
- Images: JPG, JPEG, PNG, GIF, SVG
- Archives: ZIP, RAR, 7Z
- Spreadsheets: CSV, XLSX, XLS
- Media: MP4, MOV, AVI, MP3, WAV

**File Size Limit:** 10 MB per file

### Searching and Filtering

**Search:**
- Enter keywords in the sidebar search box
- Searches across task names, descriptions, and tags

**Filters:**
- **Status** - All, Active, or Completed
- **Priority** - All, High, Medium, or Low
- **Category** - Filter by specific category
- **Tags** - Select one or more tags

Click **"Clear Filters"** to reset all filters

## 🗂️ Project Structure

```
/home/linda/projects/
├── app.py                  # Main Streamlit application
├── db_helpers.py           # Database operations
├── storage_helpers.py      # File storage operations
├── ui_components.py        # Reusable UI components
├── constants.py            # App constants and configuration
├── migration.sql           # Database schema migration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (local)
├── .env.example            # Example environment file
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 Configuration

### constants.py

Edit `constants.py` to customize:
- Priority colors and labels
- File upload limits (default: 10 MB)
- Allowed file types
- Time tracking increments
- UI icons

## 🚢 Deployment

### Deploying to Streamlit Cloud

1. **Push to GitHub** (if not already done)
   ```bash
   git add .
   git commit -m "Update with enhanced features"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click **"New app"**
   - Select your repository: `linda-aifund/todo-list`
   - Main file path: `app.py`
   - Click **"Advanced settings"**

3. **Add Secrets**
   In the Secrets section, paste:
   ```toml
   SUPABASE_URL = "your_supabase_project_url"
   SUPABASE_KEY = "your_supabase_anon_key"
   ```

4. **Deploy**
   - Click **"Deploy!"**
   - Wait for deployment to complete
   - Your app will be live at: `https://linda-aifund-todo-list.streamlit.app`

## 🛠️ Development

### Code Organization

- **app.py** - Main UI and application logic
- **db_helpers.py** - All database operations (CRUD for todos, categories, tags, subtasks, attachments)
- **storage_helpers.py** - Supabase Storage operations (upload, download, delete files)
- **ui_components.py** - Reusable UI components (badges, chips, formatters)
- **constants.py** - Configuration constants

### Adding New Features

1. Add database changes to a new migration file
2. Create helper functions in appropriate module
3. Update UI in `app.py`
4. Test thoroughly before deploying

## 📊 Database Schema

### Tables

- **todos** - Main todos table with task, description, priority, due date, category, time tracking
- **categories** - User-created categories with colors
- **tags** - User-created tags
- **todo_tags** - Junction table for many-to-many relationship
- **subtasks** - Checklist items for each todo
- **attachments** - File attachment metadata

### Storage

- **todo-attachments** bucket - Stores uploaded files organized by todo ID

## 🐛 Troubleshooting

### Database Errors

**Error: "relation 'categories' does not exist"**
- Solution: Run the `migration.sql` file in your Supabase SQL Editor

**Error: "column 'priority' does not exist"**
- Solution: The migration didn't complete. Re-run `migration.sql`

### Storage Errors

**Error: "Storage bucket not found"**
- Solution: Create the `todo-attachments` bucket in Supabase Storage dashboard

**Error: "Permission denied" when uploading**
- Solution: Check RLS policies on the storage bucket

### Connection Errors

**Error: "Please set SUPABASE_URL and SUPABASE_KEY"**
- Local: Check your `.env` file has correct credentials
- Deployed: Check Streamlit Cloud secrets are configured

## 🎯 Roadmap

Future enhancements:
- [ ] User authentication (multi-user support)
- [ ] Recurring todos
- [ ] Calendar view
- [ ] Email notifications/reminders
- [ ] Analytics dashboard
- [ ] Collaboration features
- [ ] Dark mode
- [ ] Export/import (CSV, JSON)
- [ ] Mobile app

## 📝 License

MIT

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome!

## 📧 Contact

Linda Lee - linda@aifund.ai

---

Built with ❤️ using [Streamlit](https://streamlit.io) and [Supabase](https://supabase.com)
