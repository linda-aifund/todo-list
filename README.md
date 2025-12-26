# Simple Todo App with Streamlit and Supabase

A basic todo list application built with Streamlit and Supabase, demonstrating CRUD operations.

## Features

- Add new todos
- Mark todos as complete/incomplete
- Delete todos
- Real-time updates with Supabase
- Clean and simple UI

## Prerequisites

- Python 3.10 or higher
- A Supabase account and project ([Sign up here](https://supabase.com))

## Setup Instructions

### 1. Clone or navigate to the project directory

```bash
cd /home/linda/projects
```

### 2. Activate the virtual environment

```bash
source venv/bin/activate
```

### 3. Install dependencies (if not already installed)

```bash
pip install -r requirements.txt
```

### 4. Set up Supabase

1. Go to [Supabase](https://app.supabase.com)
2. Create a new project (or use an existing one)
3. Go to the SQL Editor and run this SQL to create the todos table:

```sql
CREATE TABLE todos (
  id BIGSERIAL PRIMARY KEY,
  task TEXT NOT NULL,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

4. Get your project credentials:
   - Go to **Project Settings** > **API**
   - Copy your **Project URL**
   - Copy your **anon/public key**

### 5. Configure environment variables

1. Copy the example env file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Supabase credentials:
```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### 6. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
/home/linda/projects/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── .env               # Your environment variables (create this)
├── venv/              # Virtual environment
└── README.md          # This file
```

## Usage

1. Enter a task in the input field and click "Add Todo"
2. Check the checkbox to mark a todo as complete
3. Click the trash icon to delete a todo
4. Todos are automatically saved to your Supabase database

## Technologies Used

- **Streamlit** - Web application framework
- **Supabase** - Backend as a Service (PostgreSQL database)
- **Python-dotenv** - Environment variable management

## Troubleshooting

### "Please set SUPABASE_URL and SUPABASE_KEY" error
- Make sure you've created a `.env` file with your credentials
- Check that the values are correct (no quotes, no extra spaces)

### "Error fetching todos" or table doesn't exist
- Make sure you've run the SQL schema in your Supabase project
- Check that the table name is exactly `todos` (lowercase)

### Virtual environment not found
- Make sure you're in the `/home/linda/projects` directory
- Run `source venv/bin/activate` to activate the environment

## Next Steps

You can extend this app by:
- Adding user authentication with Supabase Auth
- Adding categories or tags to todos
- Implementing due dates and reminders
- Adding file uploads with Supabase Storage
- Deploying to Streamlit Cloud

## License

MIT
