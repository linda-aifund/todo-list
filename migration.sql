-- Enhanced Todo App Database Migration
-- This migration adds all new features while preserving existing data

-- Step 1: Add new columns to existing todos table
ALTER TABLE todos
ADD COLUMN IF NOT EXISTS description TEXT,
ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium',
ADD COLUMN IF NOT EXISTS due_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS time_spent_minutes INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS category_id BIGINT,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Add constraint for priority after column is created
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'todos_priority_check'
    ) THEN
        ALTER TABLE todos ADD CONSTRAINT todos_priority_check
        CHECK (priority IN ('low', 'medium', 'high'));
    END IF;
END $$;

-- Step 2: Create categories table
CREATE TABLE IF NOT EXISTS categories (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  color VARCHAR(7) DEFAULT '#6366F1',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default categories
INSERT INTO categories (name, color) VALUES
  ('Work', '#3B82F6'),
  ('Personal', '#10B981'),
  ('Shopping', '#F59E0B'),
  ('Health', '#EF4444')
ON CONFLICT (name) DO NOTHING;

-- Step 3: Create tags table
CREATE TABLE IF NOT EXISTS tags (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default tags
INSERT INTO tags (name) VALUES
  ('urgent'),
  ('important'),
  ('quick'),
  ('long-term')
ON CONFLICT (name) DO NOTHING;

-- Step 4: Create todo_tags junction table
CREATE TABLE IF NOT EXISTS todo_tags (
  todo_id BIGINT REFERENCES todos(id) ON DELETE CASCADE,
  tag_id BIGINT REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (todo_id, tag_id)
);

-- Step 5: Create subtasks table
CREATE TABLE IF NOT EXISTS subtasks (
  id BIGSERIAL PRIMARY KEY,
  todo_id BIGINT REFERENCES todos(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  completed BOOLEAN DEFAULT FALSE,
  position INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Step 6: Create attachments table
CREATE TABLE IF NOT EXISTS attachments (
  id BIGSERIAL PRIMARY KEY,
  todo_id BIGINT REFERENCES todos(id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT,
  mime_type VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Step 7: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_todos_category ON todos(category_id);
CREATE INDEX IF NOT EXISTS idx_todos_due_date ON todos(due_date);
CREATE INDEX IF NOT EXISTS idx_todos_priority ON todos(priority);
CREATE INDEX IF NOT EXISTS idx_todos_completed ON todos(completed);
CREATE INDEX IF NOT EXISTS idx_subtasks_todo ON subtasks(todo_id);
CREATE INDEX IF NOT EXISTS idx_attachments_todo ON attachments(todo_id);
CREATE INDEX IF NOT EXISTS idx_todo_tags_todo ON todo_tags(todo_id);
CREATE INDEX IF NOT EXISTS idx_todo_tags_tag ON todo_tags(tag_id);

-- Step 8: Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_todos_updated_at ON todos;
CREATE TRIGGER update_todos_updated_at
BEFORE UPDATE ON todos
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Step 9: Add foreign key constraint for category_id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_todos_category'
    ) THEN
        ALTER TABLE todos ADD CONSTRAINT fk_todos_category
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Migration complete!
-- Next step: Create storage bucket 'todo-attachments' in Supabase Dashboard
