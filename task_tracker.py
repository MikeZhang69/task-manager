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
        self.calendar_frame.pack(fill='both', expand=True)
        # Month/year navigation
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        nav_frame = tk.Frame(self.calendar_frame, bg=self.bg_color)
        nav_frame.pack(fill='x', pady=4)
        def prev_month():
            prev_m = month - 1
            prev_y = year
            if prev_m < 1:
                prev_m = 12
                prev_y -= 1
            self.show_calendar(prev_y, prev_m)
        def next_month():
            next_m = month + 1
            next_y = year
            if next_m > 12:
                next_m = 1
                next_y += 1
            self.show_calendar(next_y, next_m)
        tk.Button(nav_frame, text='<', command=prev_month, bg='#27272a', fg='#facc15', font=('Inter', 12, 'bold'), relief='flat', width=3).pack(side='left', padx=8)
        tk.Label(nav_frame, text=f'{year}-{month:02d}', bg=self.bg_color, fg='#f1f5f9', font=('Inter', 13, 'bold')).pack(side='left', padx=8)
        tk.Button(nav_frame, text='>', command=next_month, bg='#27272a', fg='#facc15', font=('Inter', 12, 'bold'), relief='flat', width=3).pack(side='left', padx=8)
        # Simple monthly calendar (current month)
        first_day = datetime(year, month, 1)
        start_weekday = first_day.weekday()
        days_in_month = (datetime(year, month+1, 1) - timedelta(days=1)).day if month < 12 else 31
        cal_frame = tk.Frame(self.calendar_frame, bg=self.bg_color)
        cal_frame.pack()
        day_bg = '#27272a'
        day_fg = '#f1f5f9'
        border_color = '#3f3f46'
        for i, day_name in enumerate(['Mon','Tue','Wed','Thu','Fri','Sat','Sun']):
            tk.Label(cal_frame, text=day_name, bg=day_bg, fg=day_fg, borderwidth=1, relief='solid', width=10, font=('Inter', 11, 'bold'), highlightbackground=border_color, highlightcolor=border_color, highlightthickness=1).grid(row=0, column=i, sticky='nsew')
        row = 1
        col = start_weekday
        for day in range(1, days_in_month+1):
            cell = tk.Frame(cal_frame, bg=day_bg, bd=1, relief='solid', highlightbackground=border_color, highlightcolor=border_color, highlightthickness=1, width=100, height=60)
            cell.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)
            # Day number
            tk.Label(cell, text=str(day), bg=day_bg, fg='#facc15', font=('Inter', 10, 'bold')).pack(anchor='nw', padx=2, pady=2)
            date_str = f"{year}-{month:02d}-{day:02d}"
            tasks = [t for t in self.task_manager.tasks if t.due_date == date_str]
            for t in tasks:
                fg = '#22c55e' if t.status=='done' else day_fg
                tk.Label(cell, text=f"{t.due_time or ''} {t.text}", bg=day_bg, fg=fg, font=('Inter', 10)).pack(anchor='w', padx=2)
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
        self.style.configure('Kanban.TButton', background='#27272a', foreground=self.fg_color, borderwidth=0, padding=6)
        self.style.map('Kanban.TButton', background=[('active', '#6366f1')])

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
            import functools
            top = tk.Toplevel(master)
            top.title('Pick a date')
            today = datetime.now()
            state = {'year': today.year, 'month': today.month}
            if self.date_var.get():
                try:
                    y, m, _ = map(int, self.date_var.get().split('-'))
                    state['year'], state['month'] = y, m
                except ValueError:
                    pass

            cal_frame = tk.Frame(top)
            cal_frame.pack()

            for i, day_name in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']):
                tk.Label(cal_frame, text=day_name, font=('Inter', 9)).grid(row=1, column=i)

            def update_calendar():
                year, month = state['year'], state['month']
                header.config(text=f'{year}-{month:02d}')
                # Remove only day buttons (rows >= 2)
                for widget in cal_frame.grid_slaves():
                    info = widget.grid_info()
                    if int(info['row']) >= 2:
                        widget.destroy()
                weeks = calendar.monthcalendar(year, month)  # Each week is a list of 7 ints (0=empty)
                for row_idx, week in enumerate(weeks):
                    for col_idx, day in enumerate(week):
                        if day == 0:
                            tk.Label(cal_frame, text='', width=3).grid(row=row_idx + 2, column=col_idx)
                        else:
                            def set_date(d):
                                self.date_var.set(f'{year}-{month:02d}-{d:02d}')
                                top.destroy()
                            btn = tk.Button(cal_frame, text=str(day), width=3, command=functools.partial(set_date, day))
                            btn.grid(row=row_idx + 2, column=col_idx)

            # Header and navigation (created after functions)
            header = tk.Label(cal_frame, text='', font=('Inter', 11, 'bold'))
            header.grid(row=0, column=1, columnspan=5)

            def prev_m():
                state['month'] -= 1
                if state['month'] < 1:
                    state['month'] = 12
                    state['year'] -= 1
                update_calendar()

            def next_m():
                state['month'] += 1
                if state['month'] > 12:
                    state['month'] = 1
                    state['year'] += 1
                update_calendar()

            tk.Button(cal_frame, text='<', command=prev_m).grid(row=0, column=0)
            tk.Button(cal_frame, text='>', command=next_m).grid(row=0, column=6)
            update_calendar()
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
