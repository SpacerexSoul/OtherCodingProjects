#!/usr/bin/env python3
"""
Task Management System

A comprehensive implementation of a task management system using SQLite.
Demonstrates best practices for working with SQLite in Python.
"""

import sqlite3
import os
import sys
import logging
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("task_manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class TaskManager:
    """SQLite-based task management system implementation"""
    
    def __init__(self, db_path="tasks.db"):
        """Initialize the task manager with database path"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Establish connection to the SQLite database"""
        try:
            # Connect with extended timeout to handle potential locking issues
            self.conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # Get row factory for dict-like results
            self.conn.row_factory = self._dict_factory
            
            self.cursor = self.conn.cursor()
            logging.info(f"Connected to SQLite database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            return False
    
    @staticmethod
    def _dict_factory(cursor, row):
        """Convert row to dictionary for easier handling"""
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    
    def initialize_schema(self) -> bool:
        """Create tables and indexes if they don't exist"""
        try:
            # Create categories table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                color TEXT
            )
            """)
            
            # Create tasks table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category_id INTEGER,
                priority INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_date DATE DEFAULT (date('now')),
                due_date DATE,
                completed_date DATE,
                FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
            )
            """)
            
            # Create tags table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                tag_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
            """)
            
            # Create task_tags many-to-many relationship table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_tags (
                task_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (task_id, tag_id),
                FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
            )
            """)
            
            # Create task_notes table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_notes (
                note_id INTEGER PRIMARY KEY,
                task_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
            )
            """)
            
            # Create indexes
            self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_category ON tasks(category_id)
            """)
            
            self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status)
            """)
            
            self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_due_date ON tasks(due_date)
            """)
            
            self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_priority ON tasks(priority)
            """)
            
            self.conn.commit()
            logging.info("Database schema initialized successfully")
            return True
        except sqlite3.Error as e:
            logging.error(f"Schema initialization error: {e}")
            self.conn.rollback()
            return False
    
    def add_category(self, name: str, description: Optional[str] = None, 
                    color: Optional[str] = None) -> Optional[int]:
        """
        Add a new task category
        
        Args:
            name: Category name
            description: Category description
            color: Color code for UI (e.g., #FF5733)
            
        Returns:
            int: Category ID if successful, None if failed
        """
        try:
            self.cursor.execute("""
            INSERT INTO categories (name, description, color)
            VALUES (?, ?, ?)
            """, (name, description, color))
            
            category_id = self.cursor.lastrowid
            self.conn.commit()
            logging.info(f"Added new category: {name} (ID: {category_id})")
            return category_id
        except sqlite3.IntegrityError:
            logging.error(f"Category with name '{name}' already exists")
            self.conn.rollback()
            return None
        except sqlite3.Error as e:
            logging.error(f"Error adding category: {e}")
            self.conn.rollback()
            return None
    
    def get_categories(self) -> List[Dict]:
        """
        Retrieve all task categories
        
        Returns:
            List[Dict]: List of categories
        """
        try:
            self.cursor.execute("""
            SELECT category_id, name, description, color
            FROM categories
            ORDER BY name
            """)
            
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error retrieving categories: {e}")
            return []
    
    def add_task(self, title: str, description: Optional[str] = None,
                category_id: Optional[int] = None, priority: int = 0,
                status: str = "pending", due_date: Optional[date] = None) -> Optional[int]:
        """
        Add a new task
        
        Args:
            title: Task title
            description: Task description
            category_id: Category ID (optional)
            priority: Task priority (0-5, with 5 being highest)
            status: Task status (pending, in_progress, completed, cancelled)
            due_date: Due date for the task
            
        Returns:
            int: Task ID if successful, None if failed
        """
        try:
            self.cursor.execute("""
            INSERT INTO tasks (title, description, category_id, priority, status, due_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (title, description, category_id, priority, status, due_date))
            
            task_id = self.cursor.lastrowid
            self.conn.commit()
            logging.info(f"Added new task: {title} (ID: {task_id})")
            return task_id
        except sqlite3.Error as e:
            logging.error(f"Error adding task: {e}")
            self.conn.rollback()
            return None
    
    def add_tags_to_task(self, task_id: int, tags: List[str]) -> bool:
        """
        Add tags to a task, creating any tags that don't exist
        
        Args:
            task_id: Task ID
            tags: List of tag names
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not tags:
            return True
        
        try:
            # Start a transaction
            self.conn.execute("BEGIN TRANSACTION")
            
            # For each tag: insert if not exists, then get ID
            for tag_name in tags:
                # Try to insert the tag (if it doesn't exist)
                try:
                    self.cursor.execute("""
                    INSERT INTO tags (name)
                    VALUES (?)
                    """, (tag_name,))
                    tag_id = self.cursor.lastrowid
                except sqlite3.IntegrityError:
                    # Tag already exists, get its ID
                    self.cursor.execute("""
                    SELECT tag_id FROM tags WHERE name = ?
                    """, (tag_name,))
                    tag_id = self.cursor.fetchone()["tag_id"]
                
                # Associate tag with task
                try:
                    self.cursor.execute("""
                    INSERT INTO task_tags (task_id, tag_id)
                    VALUES (?, ?)
                    """, (task_id, tag_id))
                except sqlite3.IntegrityError:
                    # Relationship already exists, continue
                    pass
            
            self.conn.commit()
            logging.info(f"Added tags {tags} to task {task_id}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding tags to task: {e}")
            self.conn.rollback()
            return False
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """
        Retrieve a task by ID with its category and tags
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict: Task data or None if not found
        """
        try:
            # Get task with category
            self.cursor.execute("""
            SELECT t.task_id, t.title, t.description, t.priority, t.status,
                   t.created_date, t.due_date, t.completed_date,
                   t.category_id, c.name as category_name, c.color as category_color
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.category_id
            WHERE t.task_id = ?
            """, (task_id,))
            
            task = self.cursor.fetchone()
            
            if not task:
                return None
            
            # Get tags for the task
            self.cursor.execute("""
            SELECT t.name
            FROM tags t
            JOIN task_tags tt ON t.tag_id = tt.tag_id
            WHERE tt.task_id = ?
            ORDER BY t.name
            """, (task_id,))
            
            tags = [row["name"] for row in self.cursor.fetchall()]
            task["tags"] = tags
            
            # Get notes for the task
            self.cursor.execute("""
            SELECT note_id, content, created_date
            FROM task_notes
            WHERE task_id = ?
            ORDER BY created_date DESC
            """, (task_id,))
            
            notes = self.cursor.fetchall()
            task["notes"] = notes
            
            return task
        except sqlite3.Error as e:
            logging.error(f"Error retrieving task: {e}")
            return None
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """
        Update task information
        
        Args:
            task_id: Task ID
            **kwargs: Fields to update (title, description, category_id, 
                     priority, status, due_date)
            
        Returns:
            bool: True if successful, False otherwise
        """
        valid_fields = ["title", "description", "category_id", 
                        "priority", "status", "due_date"]
        
        # Filter valid fields
        update_data = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        if not update_data:
            logging.warning("No valid update fields provided")
            return False
        
        # Handle status change to completed
        if update_data.get("status") == "completed":
            update_data["completed_date"] = date.today()
        
        # Build query dynamically
        placeholders = ", ".join([f"{field} = ?" for field in update_data.keys()])
        values = list(update_data.values())
        values.append(task_id)  # For the WHERE clause
        
        try:
            query = f"""
            UPDATE tasks
            SET {placeholders}
            WHERE task_id = ?
            """
            
            self.cursor.execute(query, values)
            
            if self.cursor.rowcount == 0:
                logging.warning(f"No task found with ID {task_id}")
                self.conn.rollback()
                return False
            
            self.conn.commit()
            logging.info(f"Updated task ID {task_id}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error updating task: {e}")
            self.conn.rollback()
            return False
    
    def add_note_to_task(self, task_id: int, content: str) -> Optional[int]:
        """
        Add a note to a task
        
        Args:
            task_id: Task ID
            content: Note content
            
        Returns:
            int: Note ID if successful, None if failed
        """
        try:
            self.cursor.execute("""
            INSERT INTO task_notes (task_id, content)
            VALUES (?, ?)
            """, (task_id, content))
            
            note_id = self.cursor.lastrowid
            self.conn.commit()
            logging.info(f"Added note to task {task_id}")
            return note_id
        except sqlite3.Error as e:
            logging.error(f"Error adding note to task: {e}")
            self.conn.rollback()
            return None
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task (and all associated tags and notes due to cascading)
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Delete the task (cascades to task_tags and task_notes)
            self.cursor.execute("""
            DELETE FROM tasks
            WHERE task_id = ?
            """, (task_id,))
            
            if self.cursor.rowcount == 0:
                logging.warning(f"No task found with ID {task_id}")
                self.conn.rollback()
                return False
            
            self.conn.commit()
            logging.info(f"Deleted task ID {task_id}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error deleting task: {e}")
            self.conn.rollback()
            return False
    
    def search_tasks(self, 
                   title: Optional[str] = None,
                   category_id: Optional[int] = None,
                   status: Optional[str] = None,
                   tags: Optional[List[str]] = None,
                   priority_min: Optional[int] = None,
                   priority_max: Optional[int] = None,
                   due_before: Optional[date] = None,
                   due_after: Optional[date] = None) -> List[Dict]:
        """
        Search for tasks with various filters
        
        Returns:
            List[Dict]: List of tasks matching the criteria
        """
        try:
            # Build query
            query = """
            SELECT DISTINCT t.task_id, t.title, t.status, t.priority, t.due_date,
                   c.name as category_name
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.category_id
            """
            
            # Add tag join if needed
            if tags:
                query += """
                JOIN task_tags tt ON t.task_id = tt.task_id
                JOIN tags tag ON tt.tag_id = tag.tag_id
                """
            
            conditions = []
            params = []
            
            # Add filter conditions
            if title:
                conditions.append("t.title LIKE ?")
                params.append(f"%{title}%")
            
            if category_id:
                conditions.append("t.category_id = ?")
                params.append(category_id)
            
            if status:
                conditions.append("t.status = ?")
                params.append(status)
            
            if tags:
                placeholders = ", ".join(["?"] * len(tags))
                conditions.append(f"tag.name IN ({placeholders})")
                params.extend(tags)
            
            if priority_min is not None:
                conditions.append("t.priority >= ?")
                params.append(priority_min)
            
            if priority_max is not None:
                conditions.append("t.priority <= ?")
                params.append(priority_max)
            
            if due_before:
                conditions.append("t.due_date <= ?")
                params.append(due_before)
            
            if due_after:
                conditions.append("t.due_date >= ?")
                params.append(due_after)
            
            # Add WHERE clause if we have conditions
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # Add order by
            query += " ORDER BY t.priority DESC, t.due_date ASC"
            
            # Execute query
            self.cursor.execute(query, params)
            
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error searching tasks: {e}")
            return []
    
    def get_task_counts_by_status(self) -> Dict[str, int]:
        """
        Get counts of tasks by status
        
        Returns:
            Dict[str, int]: Count of tasks for each status
        """
        try:
            self.cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM tasks
            GROUP BY status
            """)
            
            results = self.cursor.fetchall()
            return {row["status"]: row["count"] for row in results}
        except sqlite3.Error as e:
            logging.error(f"Error getting task counts: {e}")
            return {}
    
    def get_overdue_tasks(self) -> List[Dict]:
        """
        Get all overdue tasks (due date in the past and not completed)
        
        Returns:
            List[Dict]: List of overdue tasks
        """
        try:
            today = date.today()
            
            self.cursor.execute("""
            SELECT t.task_id, t.title, t.priority, t.due_date,
                   c.name as category_name
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.category_id
            WHERE t.due_date < ?
              AND t.status != 'completed'
              AND t.status != 'cancelled'
            ORDER BY t.due_date ASC
            """, (today,))
            
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting overdue tasks: {e}")
            return []
    
    def close(self):
        """Close the database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed")


def main():
    """Example usage of the TaskManager class"""
    # Initialize the task manager
    task_manager = TaskManager("tasks.db")
    
    if not task_manager.connect():
        sys.exit(1)
    
    # Initialize schema
    task_manager.initialize_schema()
    
    # Add categories
    personal_id = task_manager.add_category(
        name="Personal", 
        description="Personal tasks and errands",
        color="#FF5733"
    )
    
    work_id = task_manager.add_category(
        name="Work", 
        description="Work-related tasks and projects",
        color="#33A8FF"
    )
    
    # Add tasks
    today = date.today()
    
    # High priority work task due soon
    report_task_id = task_manager.add_task(
        title="Complete quarterly report",
        description="Finish the Q2 financial report with all required sections",
        category_id=work_id,
        priority=5,
        status="in_progress",
        due_date=today.replace(day=today.day + 2)  # Due in 2 days
    )
    
    # Add tags to the task
    task_manager.add_tags_to_task(report_task_id, ["finance", "report", "urgent"])
    
    # Add a note to the task
    task_manager.add_note_to_task(
        report_task_id,
        "Don't forget to include the new market analysis section"
    )
    
    # Medium priority personal task
    grocery_task_id = task_manager.add_task(
        title="Grocery shopping",
        description="Buy groceries for the week",
        category_id=personal_id,
        priority=3,
        status="pending",
        due_date=today.replace(day=today.day + 1)  # Due tomorrow
    )
    
    task_manager.add_tags_to_task(grocery_task_id, ["shopping", "weekly"])
    
    # Low priority work task for future
    meeting_task_id = task_manager.add_task(
        title="Prepare for team meeting",
        description="Create agenda and gather status updates",
        category_id=work_id,
        priority=2,
        status="pending",
        due_date=today.replace(day=today.day + 5)  # Due in 5 days
    )
    
    task_manager.add_tags_to_task(meeting_task_id, ["meeting", "team"])
    
    # Retrieve and display a task
    task = task_manager.get_task(report_task_id)
    if task:
        print(f"Task: {task['title']}")
        print(f"Category: {task.get('category_name', 'None')}")
        print(f"Priority: {task['priority']}")
        print(f"Status: {task['status']}")
        print(f"Due Date: {task['due_date']}")
        print(f"Tags: {', '.join(task['tags'])}")
        print("Notes:")
        for note in task['notes']:
            print(f"- {note['content']}")
    
    # Update a task
    task_manager.update_task(
        report_task_id,
        title="Complete quarterly report with executive summary",
        priority=4  # Adjusted priority
    )
    
    # Search for tasks
    print("\nSearching for high priority tasks:")
    high_priority_tasks = task_manager.search_tasks(priority_min=4)
    for task in high_priority_tasks:
        print(f"- {task['title']} (Priority: {task['priority']}, Due: {task['due_date']})")
    
    print("\nSearching for tasks with finance tag:")
    finance_tasks = task_manager.search_tasks(tags=["finance"])
    for task in finance_tasks:
        print(f"- {task['title']}")
    
    # Get task counts by status
    counts = task_manager.get_task_counts_by_status()
    print("\nTask counts by status:")
    for status, count in counts.items():
        print(f"- {status}: {count}")
    
    # Cleanup
    task_manager.close()

if __name__ == "__main__":
    main() 