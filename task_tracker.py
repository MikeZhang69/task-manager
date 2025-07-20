import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import threading
import time
from datetime import datetime, timedelta
try:
    from plyer import notification
except ImportError:
    notification = None
try:
    from playsound import playsound
except ImportError:
    playsound = None

DATA_FILE = 'tasks.json'
REMINDER_SOUND = 'reminder.wav'  # You can provide your own sound file

class Task:
    def __init__(self, id, text, status, due_date, due_time, reminder, reminder_sent=False):
        self.id = id
        self.text = text
        self.status = status
        self.due_date = due_date
        self.due_time = due_time
        self.reminder = reminder
        self.reminder_sent = reminder_sent

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Task(**d)

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.load()

    def add_task(self, task):
        self.tasks.append(task)
        self.save()

    def update_task(self, task):
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                break
        self.save()

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save()

    def save(self):
        with open(DATA_FILE, 'w') as f:
            json.dump([t.to_dict() for t in self.tasks], f)

    def load(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                self.tasks = [Task.from_dict(d) for d in json.load(f)]
        else:
            self.tasks = []

class TaskTrackerApp(tk.Tk):
    def show_calendar(self, year=None, month=None):
        self.current_view = 'calendar'
        if self.kanban_frame:
            self.kanban_frame.pack_forget()
        if self.calendar_frame:
            self.calendar_frame.destroy()
        self.calendar_frame = ttk.Frame(self.main_frame)
        self.calendar_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Month/year navigation
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
            
        nav_frame = tk.Frame(self.calendar_frame, bg=self.bg_color)
        nav_frame.pack(fill='x', pady=(0, 20))
        
        def prev_month():
            if month == 1:
                self.show_calendar(year - 1, 12)
            else:
                self.show_calendar(year, month - 1)
            
        def next_month():
            if month == 12:
                self.show_calendar(year + 1, 1)
            else:
                self.show_calendar(year, month + 1)
            
        tk.Button(nav_frame, text='<', command=prev_month, bg='#27272a', fg='#facc15', 
                 font=('Inter', 14, 'bold'), relief='flat', width=4, height=2).pack(side='left', padx=10)
        tk.Label(nav_frame, text=f'{year}-{month:02d}', bg=self.bg_color, fg='#f1f5f9', 
                font=('Inter', 18, 'bold')).pack(side='left', padx=20)
        tk.Button(nav_frame, text='>', command=next_month, bg='#27272a', fg='#facc15', 
                 font=('Inter', 14, 'bold'), relief='flat', width=4, height=2).pack(side='left', padx=10)
        
        # Calendar grid
        cal_frame = tk.Frame(self.calendar_frame, bg=self.bg_color)
        cal_frame.pack(fill='both', expand=True)
        
        # Configure grid weights for proper expansion
        for i in range(7):
            cal_frame.columnconfigure(i, weight=1)
        for i in range(7):  # 6 weeks max + header
            cal_frame.rowconfigure(i, weight=1)
        
        # Improved calendar colors
        day_bg = '#374151'          # Lighter gray for better contrast
        day_fg = '#f9fafb'          # Brighter white text
        border_color = '#6b7280'    # Lighter border
        header_bg = '#4f46e5'       # Purple header background
        header_fg = 'white'         # White header text
        
        # Day headers
        for i, day_name in enumerate(['Mon','Tue','Wed','Thu','Fri','Sat','Sun']):
            header_label = tk.Label(cal_frame, text=day_name, bg=header_bg, fg=header_fg, 
                                  borderwidth=1, relief='solid', font=('Inter', 12, 'bold'), 
                                  highlightbackground=border_color, highlightcolor=border_color, 
                                  highlightthickness=1, height=2)
            header_label.grid(row=0, column=i, sticky='nsew', padx=1, pady=1)
        
        # Calculate calendar layout
        first_day = datetime(year, month, 1)
        start_weekday = first_day.weekday()
        
        # Get correct days in month
        if month == 12:
            days_in_month = (datetime(year + 1, 1, 1) - timedelta(days=1)).day
        else:
            days_in_month = (datetime(year, month + 1, 1) - timedelta(days=1)).day
        
        # Create calendar cells
        row = 1
        col = start_weekday
        
        for day in range(1, days_in_month + 1):
            cell = tk.Frame(cal_frame, bg=day_bg, bd=1, relief='solid', 
                          highlightbackground=border_color, highlightcolor=border_color, 
                          highlightthickness=1)
            cell.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)
            
            # Day number
            day_label = tk.Label(cell, text=str(day), bg=day_bg, fg='#fbbf24', 
                               font=('Inter', 14, 'bold'))
            day_label.pack(anchor='nw', padx=4, pady=4)
            
            # Tasks for this day
            date_str = f"{year}-{month:02d}-{day:02d}"
            tasks = [t for t in self.task_manager.tasks if t.due_date == date_str]
            
            # Create scrollable frame for tasks if there are many
            if tasks:
                task_frame = tk.Frame(cell, bg=day_bg)
                task_frame.pack(fill='both', expand=True, padx=2, pady=2)
                
                for t in tasks[:3]:  # Show max 3 tasks to avoid overcrowding
                    fg = '#22c55e' if t.status == 'done' else day_fg
                    task_text = f"{t.due_time or ''} {t.text}"
                    if len(task_text) > 15:
                        task_text = task_text[:12] + "..."
                    tk.Label(task_frame, text=task_text, bg=day_bg, fg=fg, 
                           font=('Inter', 9), wraplength=120).pack(anchor='w', pady=1)
                
                if len(tasks) > 3:
                    tk.Label(task_frame, text=f"+{len(tasks)-3} more", bg=day_bg, 
                           fg='#a1a1aa', font=('Inter', 8)).pack(anchor='w')
            
            col += 1
            if col > 6:
                col = 0
                row += 1

    def _setup_highlight_style(self):
        # Add a highlight style for drag-over columns
        self.style.configure('Highlight.TLabelframe', background='#27272a', foreground='#facc15', borderwidth=3)
        self.style.configure('Highlight.TLabelframe.Label', background='#27272a', foreground='#facc15')
    def __init__(self):
        super().__init__()
        self.title('Task Tracker')
        self.geometry('900x600')
        self.task_manager = TaskManager()
        self.current_view = 'kanban'
        self.create_widgets()
        self.reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
        self.reminder_thread.start()

    def create_widgets(self):
        self.style = ttk.Style(self)
        self._setup_highlight_style()
        # Set dark theme colors
        self.bg_color = '#18181b'
        self.fg_color = '#f1f5f9'
        self.column_colors = {
            'todo': '#ef4444',        # red
            'inprogress': '#facc15',  # yellow
            'done': '#22c55e'         # green
        }
        self.configure(bg=self.bg_color)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('Kanban.TLabelframe', background=self.bg_color, foreground=self.fg_color, borderwidth=0)
        self.style.configure('Kanban.TLabelframe.Label', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('Kanban.TButton', background='#4f46e5', foreground='white', borderwidth=1, padding=8)
        self.style.map('Kanban.TButton', 
                      background=[('active', '#6366f1'), ('pressed', '#3730a3')],
                      foreground=[('active', 'white'), ('pressed', 'white')])

        # View switcher
        top_frame = ttk.Frame(self, style='TFrame')
        top_frame.pack(fill='x', pady=5)
        ttk.Button(top_frame, text='Kanban', command=self.show_kanban, style='Kanban.TButton').pack(side='left', padx=5)
        ttk.Button(top_frame, text='Calendar', command=self.show_calendar, style='Kanban.TButton').pack(side='left', padx=5)
        ttk.Button(top_frame, text='Add Task', command=self.add_task_dialog, style='Kanban.TButton').pack(side='right', padx=5)
        self.main_frame = ttk.Frame(self, style='TFrame')
        self.main_frame.pack(fill='both', expand=True)
        self.kanban_frame = None
        self.calendar_frame = None
        self.show_kanban()

    def show_kanban(self):
        self.current_view = 'kanban'
        if self.calendar_frame:
            self.calendar_frame.pack_forget()
        if self.kanban_frame:
            self.kanban_frame.destroy()
        self.kanban_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.kanban_frame.pack(fill='both', expand=True)
        self.drag_data = {'task': None, 'widget': None}
        self.kanban_columns = {}
        columns = [
            ('To Do', 'todo'),
            ('In Progress', 'inprogress'),
            ('Done', 'done')
        ]
        for i, (col, status) in enumerate(columns):
            col_frame = ttk.LabelFrame(self.kanban_frame, text=col, style='Kanban.TLabelframe')
            col_frame.grid(row=0, column=i, sticky='nsew', padx=16, pady=16, ipadx=4, ipady=4)
            self.kanban_frame.columnconfigure(i, weight=1)
            # Color header
            header = tk.Label(col_frame, text=col, bg=self.column_colors[status], fg='#18181b', font=('Inter', 14, 'bold'), pady=8, padx=8)
            header.pack(fill='x', padx=0, pady=(0, 8))
            # Store reference for drop
            self.kanban_columns[status] = col_frame
            # List tasks
            tasks = [t for t in self.task_manager.tasks if t.status == status]
            tasks.sort(key=lambda t: (t.due_date, t.due_time or '00:00'))
            for task in tasks:
                self.create_task_widget(col_frame, task, status)

    def create_task_widget(self, parent, task, status):
        frame = tk.Frame(parent, bg='#27272a', bd=0, relief='ridge', highlightthickness=2, highlightbackground='#3f3f46')
        frame.pack(fill='x', pady=6, padx=4, ipady=4)
        # Task text
        label = tk.Label(frame, text=task.text, bg='#27272a', fg='#f1f5f9', font=('Inter', 12, 'bold'))
        label.pack(side='top', anchor='w', padx=6, pady=(2,0))
        # Info row
        info_frame = tk.Frame(frame, bg='#27272a')
        info_frame.pack(side='top', fill='x', padx=6, pady=(0,2))
        info = f"{task.due_date} {task.due_time or ''}"
        tk.Label(info_frame, text=info, bg='#27272a', fg='#a1a1aa', font=('Inter', 10)).pack(side='left')
        if task.reminder:
            tk.Label(info_frame, text='🔔', bg='#27272a', fg='#fde047', font=('Inter', 10)).pack(side='left', padx=4)
        # Action buttons
        btn_frame = tk.Frame(frame, bg='#27272a')
        btn_frame.pack(side='top', anchor='e', padx=6, pady=(0,2))
        from tkinter import ttk
        ttk.Button(btn_frame, text='Edit', command=lambda: self.edit_task_dialog(task), style='Kanban.TButton').pack(side='right', padx=2)
        ttk.Button(btn_frame, text='Delete', command=lambda: self.delete_task(task), style='Kanban.TButton').pack(side='right', padx=2)

        # --- Improved Drag-and-drop events with visual feedback ---
        def on_drag_start(event, t=task, w=frame):
            self.drag_data['task'] = t
            self.drag_data['widget'] = w
            w.config(bg='#6366f1', highlightbackground='#facc15', highlightcolor='#facc15')
            w.lift()

        def on_drag_motion(event, w=frame):
            # Highlight column under cursor
            x_root, y_root = event.x_root, event.y_root
            for col_status, col_frame in self.kanban_columns.items():
                col_x = col_frame.winfo_rootx()
                col_y = col_frame.winfo_rooty()
                col_w = col_frame.winfo_width()
                col_h = col_frame.winfo_height()
                if col_x <= x_root <= col_x + col_w and col_y <= y_root <= col_y + col_h:
                    col_frame.config(style='Highlight.TLabelframe')
                else:
                    col_frame.config(style='Kanban.TLabelframe')

        def on_drag_end(event, w=frame):
            x_root = event.x_root
            y_root = event.y_root
            dropped = False
            for col_status, col_frame in self.kanban_columns.items():
                col_x = col_frame.winfo_rootx()
                col_y = col_frame.winfo_rooty()
                col_w = col_frame.winfo_width()
                col_h = col_frame.winfo_height()
                # Remove highlight
                col_frame.config(style='Kanban.TLabelframe')
                if col_x <= x_root <= col_x + col_w and col_y <= y_root <= col_y + col_h:
                    if self.drag_data['task'] and self.drag_data['task'].status != col_status:
                        self.move_task(self.drag_data['task'], col_status)
                    dropped = True
                    break
            # Reset drag state and color
            if self.drag_data['widget']:
                self.drag_data['widget'].config(bg='#27272a', highlightbackground='#3f3f46', highlightcolor='#3f3f46')
            self.drag_data['task'] = None
            self.drag_data['widget'] = None

        frame.bind('<ButtonPress-1>', on_drag_start)
        frame.bind('<B1-Motion>', on_drag_motion)
        frame.bind('<ButtonRelease-1>', on_drag_end)

    def _on_drag_motion(self, event, frame):
        # Optionally, add visual feedback for dragging
        pass

    def _on_column_enter(self, event, status):
        # If dragging, move task to this column
        if self.drag_data['task']:
            self.move_task(self.drag_data['task'], status)
            # Reset drag state
            if self.drag_data['widget']:
                self.drag_data['widget'].config(bg='#27272a')
            self.drag_data['task'] = None
            self.drag_data['widget'] = None

    def _on_column_leave(self, event, status):
        # Optional: visual feedback for leaving column
        pass

    def move_task(self, task, new_status):
        task.status = new_status
        self.task_manager.update_task(task)
        self.show_kanban()
        if new_status == 'done':
            self.celebrate()



    def add_task_dialog(self):
        TaskDialog(self, self.task_manager, on_save=self.on_task_added)

    def edit_task_dialog(self, task):
        TaskDialog(self, self.task_manager, task=task, on_save=self.on_task_edited)

    def delete_task(self, task):
        if messagebox.askyesno('Delete Task', 'Are you sure you want to delete this task?'):
            self.task_manager.delete_task(task.id)
            self.show_kanban() if self.current_view == 'kanban' else self.show_calendar()

    def on_task_added(self, task):
        self.task_manager.add_task(task)
        self.show_kanban() if self.current_view == 'kanban' else self.show_calendar()

    def on_task_edited(self, task):
        self.task_manager.update_task(task)
        self.show_kanban() if self.current_view == 'kanban' else self.show_calendar()

    def celebrate(self):
        # Play sound or show message
        if playsound and os.path.exists(REMINDER_SOUND):
            threading.Thread(target=playsound, args=(REMINDER_SOUND,), daemon=True).start()
        else:
            messagebox.showinfo('Congratulations!', 'Task completed! 🎉')

    def reminder_loop(self):
        while True:
            now = datetime.now()
            for task in self.task_manager.tasks:
                if task.reminder and not task.reminder_sent and task.status != 'done':
                    due = datetime.strptime(f"{task.due_date} {task.due_time or '00:00'}", "%Y-%m-%d %H:%M")
                    diff = (due - now).total_seconds()
                    if 0 < diff <= 900:
                        self.send_reminder(task)
                        task.reminder_sent = True
                        self.task_manager.update_task(task)
            time.sleep(30)

    def send_reminder(self, task):
        if notification:
            notification.notify(
                title='Task Reminder',
                message=f'Your task "{task.text}" is due in 15 minutes.',
                app_name='Task Tracker'
            )
        if playsound and os.path.exists(REMINDER_SOUND):
            threading.Thread(target=playsound, args=(REMINDER_SOUND,), daemon=True).start()

class TaskDialog(simpledialog.Dialog):
    def __init__(self, parent, task_manager, task=None, on_save=None):
        self.task_manager = task_manager
        self.task = task
        self.on_save = on_save
        super().__init__(parent, title='Edit Task' if task else 'Add Task')

    def body(self, master):
        import calendar
        tk.Label(master, text='Task:').grid(row=0, column=0)
        self.text_var = tk.StringVar(value=self.task.text if self.task else '')
        tk.Entry(master, textvariable=self.text_var).grid(row=0, column=1)
        tk.Label(master, text='Due Date:').grid(row=1, column=0)
        self.date_var = tk.StringVar(value=self.task.due_date if self.task else datetime.now().strftime('%Y-%m-%d'))
        date_entry = tk.Entry(master, textvariable=self.date_var)
        date_entry.grid(row=1, column=1, sticky='w')
        def pick_date():
            top = tk.Toplevel(master)
            top.title('Select Date')
            top.geometry('400x280')
            top.resizable(False, False)
            top.grab_set()  # Make it modal
            top.configure(bg='#18181b')
            
            # Center the window
            top.transient(master)
            
            main_frame = tk.Frame(top, bg='#18181b')
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Title
            title_label = tk.Label(main_frame, text='Select Date', font=('Inter', 16, 'bold'),
                                 bg='#18181b', fg='#f1f5f9')
            title_label.pack(pady=(0, 20))
            
            # Date selection frame
            date_frame = tk.Frame(main_frame, bg='#18181b')
            date_frame.pack(pady=10)
            
            # Get current date or default
            current_date = datetime.now()
            if self.date_var.get():
                try:
                    current_date = datetime.strptime(self.date_var.get(), '%Y-%m-%d')
                except ValueError:
                    pass
            
            # Year selection
            tk.Label(date_frame, text='Year:', bg='#18181b', fg='#f1f5f9', 
                    font=('Inter', 12)).grid(row=0, column=0, padx=10, pady=8, sticky='e')
            year_var = tk.StringVar(value=str(current_date.year))
            year_spinbox = tk.Spinbox(date_frame, from_=2020, to=2030, textvariable=year_var,
                                    width=10, font=('Inter', 12), bg='#27272a', fg='#f1f5f9',
                                    buttonbackground='#27272a', relief='solid', bd=1)
            year_spinbox.grid(row=0, column=1, padx=10, pady=8)
            
            # Month selection
            tk.Label(date_frame, text='Month:', bg='#18181b', fg='#f1f5f9',
                    font=('Inter', 12)).grid(row=1, column=0, padx=10, pady=8, sticky='e')
            month_var = tk.StringVar(value=str(current_date.month))
            month_spinbox = tk.Spinbox(date_frame, from_=1, to=12, textvariable=month_var,
                                     width=10, font=('Inter', 12), bg='#27272a', fg='#f1f5f9',
                                     buttonbackground='#27272a', relief='solid', bd=1)
            month_spinbox.grid(row=1, column=1, padx=10, pady=8)
            
            # Day selection
            tk.Label(date_frame, text='Day:', bg='#18181b', fg='#f1f5f9',
                    font=('Inter', 12)).grid(row=2, column=0, padx=10, pady=8, sticky='e')
            day_var = tk.StringVar(value=str(current_date.day))
            day_spinbox = tk.Spinbox(date_frame, from_=1, to=31, textvariable=day_var,
                                   width=10, font=('Inter', 12), bg='#27272a', fg='#f1f5f9',
                                   buttonbackground='#27272a', relief='solid', bd=1)
            day_spinbox.grid(row=2, column=1, padx=10, pady=8)
            
            # Buttons
            btn_frame = tk.Frame(main_frame, bg='#18181b')
            btn_frame.pack(pady=(30, 0))
            
            def set_today():
                today = datetime.now()
                year_var.set(str(today.year))
                month_var.set(str(today.month))
                day_var.set(str(today.day))
            
            def apply_date():
                try:
                    year = int(year_var.get())
                    month = int(month_var.get())
                    day = int(day_var.get())
                    # Validate date
                    selected_date = datetime(year, month, day)
                    self.date_var.set(selected_date.strftime('%Y-%m-%d'))
                    top.destroy()
                except ValueError:
                    messagebox.showerror('Invalid Date', 'Please enter a valid date.')
                except Exception as e:
                    messagebox.showerror('Error', f'An error occurred: {str(e)}')
            
            # Create buttons with highly visible text
            today_btn = tk.Button(btn_frame, text='Today', command=set_today,
                                bg='lightblue', fg='black', font=('Arial', 14, 'bold'), 
                                relief='raised', bd=3, padx=20, pady=10, cursor='hand2',
                                activebackground='blue', activeforeground='white')
            today_btn.pack(side='left', padx=10)
            
            ok_btn = tk.Button(btn_frame, text='OK', command=apply_date,
                             bg='lightgreen', fg='black', font=('Arial', 14, 'bold'), 
                             relief='raised', bd=3, padx=25, pady=10, cursor='hand2',
                             activebackground='green', activeforeground='white')
            ok_btn.pack(side='left', padx=10)
            
            cancel_btn = tk.Button(btn_frame, text='Cancel', command=top.destroy,
                                 bg='lightcoral', fg='black', font=('Arial', 14, 'bold'), 
                                 relief='raised', bd=3, padx=20, pady=10, cursor='hand2',
                                 activebackground='red', activeforeground='white')
            cancel_btn.pack(side='left', padx=10)
            
            # Focus on OK button and bind Enter key
            ok_btn.focus_set()
            top.bind('<Return>', lambda e: apply_date())
            top.bind('<Escape>', lambda e: top.destroy())
        tk.Button(master, text='Pick', command=pick_date).grid(row=1, column=2, padx=2)
        tk.Label(master, text='Due Time (HH:MM):').grid(row=2, column=0)
        self.time_var = tk.StringVar(value=self.task.due_time if self.task else datetime.now().strftime('%H:%M'))
        tk.Entry(master, textvariable=self.time_var).grid(row=2, column=1)
        self.reminder_var = tk.BooleanVar(value=self.task.reminder if self.task else False)
        tk.Checkbutton(master, text='Set Reminder (15 min before)', variable=self.reminder_var).grid(row=3, columnspan=2)
        return master

    def apply(self):
        text = self.text_var.get().strip()
        due_date = self.date_var.get().strip()
        due_time = self.time_var.get().strip()
        reminder = self.reminder_var.get()
        if not text or not due_date:
            messagebox.showerror('Error', 'Task and due date are required.')
            return
        task_id = self.task.id if self.task else f"task-{int(time.time()*1000)}"
        reminder_sent = self.task.reminder_sent if self.task else False
        status = self.task.status if self.task else 'todo'
        task = Task(task_id, text, status, due_date, due_time, reminder, reminder_sent)
        if self.on_save:
            self.on_save(task)

if __name__ == '__main__':
    app = TaskTrackerApp()
    app.mainloop()
