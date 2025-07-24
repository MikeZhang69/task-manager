import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
import threading
import time

class TaskTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kanban & Calendar Task Tracker")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Data storage
        self.tasks = []
        self.current_view = "kanban"
        self.current_month = datetime.now().replace(day=1)
        self.task_to_delete = None
        
        # Load tasks
        self.load_tasks()
        
        # Create UI
        self.create_widgets()
        self.render()
        
        # Start reminder checker
        self.start_reminder_checker()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = tk.Label(header_frame, text="Task Tracker", font=("Arial", 24, "bold"), bg="#f0f0f0")
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Kanban & Calendar View", font=("Arial", 12), bg="#f0f0f0", fg="#666")
        subtitle_label.pack()
        
        # View toggle buttons
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.kanban_btn = tk.Button(button_frame, text="Kanban Board", font=("Arial", 12), 
                                   bg="#3b82f6", fg="white", command=lambda: self.switch_view("kanban"))
        self.kanban_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.calendar_btn = tk.Button(button_frame, text="Calendar View", font=("Arial", 12), 
                                     bg="#e0e0e0", command=lambda: self.switch_view("calendar"))
        self.calendar_btn.pack(side=tk.LEFT)
        
        # Main content frame
        self.content_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Kanban view
        self.kanban_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        self.create_kanban_view()
        
        # Calendar view
        self.calendar_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        self.create_calendar_view()
        
        # Add task button
        add_task_btn = tk.Button(self.root, text="+ Add New Task", font=("Arial", 12), 
                                bg="#3b82f6", fg="white", command=self.open_task_dialog)
        add_task_btn.pack(pady=10)
        
        # Task dialog
        self.task_dialog = None
        self.delete_dialog = None
    
    def create_kanban_view(self):
        # Create columns
        columns_frame = tk.Frame(self.kanban_frame, bg="#f0f0f0")
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        # To Do column
        self.todo_frame = self.create_column(columns_frame, "To Do", "#3b82f6", 0)
        
        # In Progress column
        self.inprogress_frame = self.create_column(columns_frame, "In Progress", "#f59e0b", 1)
        
        # Done column
        self.done_frame = self.create_column(columns_frame, "Done", "#10b981", 2)
    
    def create_column(self, parent, title, color, column):
        frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        frame.grid(row=0, column=column, sticky="nsew", padx=5)
        parent.grid_columnconfigure(column, weight=1)
        
        # Header
        header = tk.Frame(frame, bg=color, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text=title, font=("Arial", 14, "bold"), bg=color, fg="white")
        title_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.count_labels = getattr(self, 'count_labels', {})
        count_label = tk.Label(header, text="0", font=("Arial", 12), bg=color, fg="white")
        count_label.pack(side=tk.RIGHT, padx=10, pady=5)
        self.count_labels[title.lower().replace(" ", "")] = count_label
        
        # Tasks container
        tasks_container = tk.Frame(frame, bg="white")
        tasks_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(tasks_container, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(tasks_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        setattr(self, f"{title.lower().replace(' ', '')}_canvas", canvas)
        setattr(self, f"{title.lower().replace(' ', '')}_frame", scrollable_frame)
        
        return frame
    
    def create_calendar_view(self):
        # Calendar header
        header_frame = tk.Frame(self.calendar_frame, bg="white")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.month_label = tk.Label(header_frame, text="", font=("Arial", 18, "bold"), bg="white")
        self.month_label.pack(side=tk.LEFT, padx=10)
        
        nav_frame = tk.Frame(header_frame, bg="white")
        nav_frame.pack(side=tk.RIGHT, padx=10)
        
        prev_btn = tk.Button(nav_frame, text="<", font=("Arial", 12), command=self.previous_month)
        prev_btn.pack(side=tk.LEFT, padx=5)
        
        next_btn = tk.Button(nav_frame, text=">", font=("Arial", 12), command=self.next_month)
        next_btn.pack(side=tk.LEFT, padx=5)
        
        # Calendar grid
        self.calendar_grid = tk.Frame(self.calendar_frame, bg="white")
        self.calendar_grid.pack(fill=tk.BOTH, expand=True)
        
        # Days of week header
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            label = tk.Label(self.calendar_grid, text=day, font=("Arial", 10, "bold"), 
                            bg="#e0e0e0", width=10, height=2)
            label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
        
        # Calendar days grid
        self.calendar_days = []
        for row in range(1, 7):
            for col in range(7):
                day_frame = tk.Frame(self.calendar_grid, bg="white", relief=tk.RAISED, bd=1)
                day_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                self.calendar_grid.grid_columnconfigure(col, weight=1)
                self.calendar_grid.grid_rowconfigure(row, weight=1)
                self.calendar_days.append(day_frame)
    
    def switch_view(self, view):
        self.current_view = view
        
        if view == "kanban":
            self.kanban_frame.pack(fill=tk.BOTH, expand=True)
            self.calendar_frame.pack_forget()
            self.kanban_btn.configure(bg="#3b82f6", fg="white")
            self.calendar_btn.configure(bg="#e0e0e0", fg="black")
        else:
            self.calendar_frame.pack(fill=tk.BOTH, expand=True)
            self.kanban_frame.pack_forget()
            self.calendar_btn.configure(bg="#3b82f6", fg="white")
            self.kanban_btn.configure(bg="#e0e0e0", fg="black")
        
        self.render()
    
    def render(self):
        if self.current_view == "kanban":
            self.render_kanban_board()
        else:
            self.render_calendar()
    
    def render_kanban_board(self):
        # Clear task containers
        for status in ["todo", "inprogress", "done"]:
            container = getattr(self, f"{status}_frame")
            for widget in container.winfo_children():
                widget.destroy()
        
        # Sort tasks by date
        sorted_tasks = sorted(self.tasks, key=lambda x: x.get("date", ""))
        
        # Render tasks in their respective columns
        for task in sorted_tasks:
            self.render_task_card(task)
        
        # Update task counts
        self.update_task_counts()
    
    def render_task_card(self, task):
        status = task.get("status", "todo")
        container = getattr(self, f"{status}_frame")
        
        card = tk.Frame(container, bg="white", relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, pady=5, padx=5)
        
        # Task title
        title_label = tk.Label(card, text=task.get("title", ""), font=("Arial", 11, "bold"), 
                              bg="white", anchor="w")
        title_label.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Task details
        date_str = task.get("date", "")
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%b %d")
                time_str = task.get("time", "")
                if time_str:
                    detail_text = f"{formatted_date} at {time_str}"
                else:
                    detail_text = formatted_date
                
                detail_label = tk.Label(card, text=detail_text, font=("Arial", 9), 
                                       bg="white", fg="#666")
                detail_label.pack(anchor="w", padx=5)
            except ValueError:
                pass
        
        # Buttons frame
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        edit_btn = tk.Button(btn_frame, text="Edit", font=("Arial", 8), 
                            command=lambda t=task: self.open_task_dialog(t))
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_btn = tk.Button(btn_frame, text="Delete", font=("Arial", 8), 
                              command=lambda t=task: self.open_delete_dialog(t))
        delete_btn.pack(side=tk.LEFT)
    
    def update_task_counts(self):
        counts = {"todo": 0, "inprogress": 0, "done": 0}
        for task in self.tasks:
            status = task.get("status", "todo")
            if status in counts:
                counts[status] += 1
        
        for status, count in counts.items():
            label = self.count_labels.get(status)
            if label:
                label.configure(text=str(count))
    
    def render_calendar(self):
        # Update month/year display
        self.month_label.configure(text=self.current_month.strftime("%B %Y"))
        
        # Clear calendar days
        for day_frame in self.calendar_days:
            for widget in day_frame.winfo_children():
                widget.destroy()
        
        # Get first day of month and number of days
        year = self.current_month.year
        month = self.current_month.month
        first_day = self.current_month.weekday()  # Monday is 0, Sunday is 6
        days_in_month = (self.current_month.replace(month=month % 12 + 1, day=1) - 
                        timedelta(days=1)).day
        
        # Add days to calendar
        day_counter = 1
        for i, day_frame in enumerate(self.calendar_days):
            # Skip days before the first day of the month
            if i < first_day:
                continue
            
            # Stop when we've added all days of the month
            if day_counter > days_in_month:
                break
            
            # Day number
            day_label = tk.Label(day_frame, text=str(day_counter), font=("Arial", 10, "bold"), 
                                bg="white")
            day_label.pack(anchor="nw", padx=2, pady=2)
            
            # Tasks for this day
            date_str = f"{year}-{month:02d}-{day_counter:02d}"
            day_tasks = [t for t in self.tasks if t.get("date") == date_str]
            
            for task in day_tasks[:3]:  # Show only first 3 tasks
                status = task.get("status", "todo")
                color = {"todo": "#3b82f6", "inprogress": "#f59e0b", "done": "#10b981"}.get(status, "#666")
                
                task_label = tk.Label(day_frame, text=task.get("title", "")[:15], 
                                     font=("Arial", 8), bg=color, fg="white", anchor="w")
                task_label.pack(fill=tk.X, padx=2, pady=1)
            
            if len(day_tasks) > 3:
                more_label = tk.Label(day_frame, text=f"+{len(day_tasks) - 3} more", 
                                     font=("Arial", 8), bg="white", fg="#666")
                more_label.pack(anchor="w", padx=2)
            
            day_counter += 1
    
    def open_task_dialog(self, task=None):
        if self.task_dialog:
            self.task_dialog.destroy()
        
        self.task_dialog = tk.Toplevel(self.root)
        self.task_dialog.title("Add/Edit Task" if not task else "Edit Task")
        self.task_dialog.geometry("400x350")
        self.task_dialog.configure(bg="white")
        self.task_dialog.resizable(False, False)
        
        # Center the dialog
        self.task_dialog.transient(self.root)
        self.task_dialog.grab_set()
        
        # Task data
        task_id = task.get("id") if task else None
        title = task.get("title", "") if task else ""
        date = task.get("date", datetime.now().strftime("%Y-%m-%d")) if task else datetime.now().strftime("%Y-%m-%d")
        time_val = task.get("time", "") if task else ""
        status = task.get("status", "todo") if task else "todo"
        reminder = task.get("reminder", False) if task else False
        
        # Title
        tk.Label(self.task_dialog, text="Task Title:", font=("Arial", 10), bg="white").pack(anchor="w", padx=20, pady=(20, 5))
        title_entry = tk.Entry(self.task_dialog, font=("Arial", 10))
        title_entry.insert(0, title)
        title_entry.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Date and Time
        date_frame = tk.Frame(self.task_dialog, bg="white")
        date_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(date_frame, text="Due Date:", font=("Arial", 10), bg="white").pack(side=tk.LEFT)
        date_entry = tk.Entry(date_frame, font=("Arial", 10), width=12)
        date_entry.insert(0, date)
        date_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Label(date_frame, text="Time:", font=("Arial", 10), bg="white").pack(side=tk.LEFT, padx=(20, 5))
        time_entry = tk.Entry(date_frame, font=("Arial", 10), width=8)
        time_entry.insert(0, time_val)
        time_entry.pack(side=tk.LEFT)
        
        # Status
        tk.Label(self.task_dialog, text="Status:", font=("Arial", 10), bg="white").pack(anchor="w", padx=20, pady=(10, 5))
        status_var = tk.StringVar(value=status)
        status_combo = ttk.Combobox(self.task_dialog, textvariable=status_var, 
                                   values=["todo", "inprogress", "done"], state="readonly")
        status_combo.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Reminder
        reminder_var = tk.BooleanVar(value=reminder)
        reminder_check = tk.Checkbutton(self.task_dialog, text="Set Reminder (15 minutes before)", 
                                       variable=reminder_var, bg="white", font=("Arial", 10))
        reminder_check.pack(anchor="w", padx=20, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self.task_dialog, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 10), 
                              command=self.task_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        save_btn = tk.Button(btn_frame, text="Save Task", font=("Arial", 10), bg="#3b82f6", fg="white",
                            command=lambda: self.save_task(
                                task_id, title_entry.get(), date_entry.get(), 
                                time_entry.get(), status_var.get(), reminder_var.get()
                            ))
        save_btn.pack(side=tk.RIGHT)
    
    def save_task(self, task_id, title, date, time_val, status, reminder):
        if not title:
            messagebox.showerror("Error", "Task title is required")
            return
        
        if task_id:
            # Update existing task
            for i, task in enumerate(self.tasks):
                if task.get("id") == task_id:
                    self.tasks[i] = {
                        "id": task_id,
                        "title": title,
                        "date": date,
                        "time": time_val,
                        "status": status,
                        "reminder": reminder
                    }
                    break
        else:
            # Add new task
            new_task = {
                "id": str(int(time.time() * 1000)),
                "title": title,
                "date": date,
                "time": time_val,
                "status": status,
                "reminder": reminder
            }
            self.tasks.append(new_task)
        
        self.save_tasks()
        self.render()
        self.task_dialog.destroy()
    
    def open_delete_dialog(self, task):
        result = messagebox.askyesno("Confirm Delete", 
                                    f"Are you sure you want to delete '{task.get('title', '')}'?")
        if result:
            self.tasks = [t for t in self.tasks if t.get("id") != task.get("id")]
            self.save_tasks()
            self.render()
    
    def previous_month(self):
        self.current_month = (self.current_month - timedelta(days=1)).replace(day=1)
        self.render_calendar()
    
    def next_month(self):
        if self.current_month.month == 12:
            self.current_month = self.current_month.replace(year=self.current_month.year + 1, month=1)
        else:
            self.current_month = self.current_month.replace(month=self.current_month.month + 1)
        self.render_calendar()
    
    def load_tasks(self):
        try:
            if os.path.exists("tasks.json"):
                with open("tasks.json", "r") as f:
                    self.tasks = json.load(f)
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []
    
    def save_tasks(self):
        try:
            with open("tasks.json", "w") as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def start_reminder_checker(self):
        def check_reminders():
            while True:
                self.check_reminders()
                time.sleep(30)  # Check every 30 seconds
        
        thread = threading.Thread(target=check_reminders, daemon=True)
        thread.start()
    
    def check_reminders(self):
        now = datetime.now()
        fifteen_minutes_later = now + timedelta(minutes=15)
        
        for task in self.tasks:
            if task.get("reminder"):
                date_str = task.get("date")
                time_str = task.get("time")
                if date_str and time_str:
                    try:
                        task_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                        if now <= task_datetime <= fifteen_minutes_later:
                            # Show reminder (in a real app, this would be a system notification)
                            print(f"Reminder: {task.get('title')}")
                    except ValueError:
                        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTrackerApp(root)
    root.mainloop()
