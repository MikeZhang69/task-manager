
# Kanban & Calendar Task Tracker

This is a feature-rich, single-page web application designed for comprehensive task management. It combines a traditional Kanban board with a calendar view, allowing users to organize their workflow and schedule tasks with precision. The app is enhanced with AI-powered features, persistent local storage, and user-friendly notifications.

## ✨ Features

This application is built with vanilla HTML, CSS (using Tailwind CSS), and JavaScript, and it includes the following key features:

### Core Task Management

- **Kanban Board:** A classic three-column layout ("To Do", "In Progress", "Done") for a clear visual workflow.
- **Drag & Drop:** Intuitively move tasks between columns to update their status.
- **Full CRUD Operations:**
  - **Create:** Add new tasks with a title, due date, due time, and an optional reminder.
  - **Read:** View all tasks on the Kanban board or in the calendar.
  - **Update:** Edit any existing task's details through a dedicated modal.
  - **Delete:** Remove tasks with a confirmation step to prevent accidental deletion.
- **Confetti Celebration:** A fun confetti animation plays whenever a task is moved to the "Done" column.

### Scheduling & Organization

- **Calendar View:** A full monthly calendar that displays all tasks on their respective due dates, color-coded by status.
- **Date & Time Precision:** Assign a specific due date and time to each task for granular scheduling.
- **Chronological Sorting:** Tasks on the Kanban board are automatically sorted by their due date and time, ensuring the most urgent items are always at the top.

### AI & Notifications

- **Gemini AI Task Breakdown:** Enter a large, complex project, and the app uses the Gemini API to automatically break it down into smaller, actionable sub-tasks.
- **Task Reminders:** Set an alarm for any task to receive a browser notification 15 minutes before it's due.

### Usability & Persistence

- **Local Storage:** All tasks are automatically saved to the browser's `localStorage`, so your data persists even after closing or refreshing the page.
- **Smart Defaults:** The date and time pickers automatically default to the current date and time for quick task creation.
- **Responsive Design:** The interface is designed to be fully usable on both desktop and mobile devices.

## 🚀 How to Use

- **Save the File:** Copy the entire HTML code into a plain text editor (like Notepad, VS Code, or TextEdit) and save it with an `.html` extension (e.g., `task-tracker.html`).
- **Open in Browser:** Locate the saved file on your computer and double-click it to open it in any modern web browser (like Chrome, Firefox, or Safari).

### Adding a Task

1. Enter the task description in the **"Enter a new task..."** field.
2. Select a due date and time.
3. Check the **"Set Reminder"** box if you want a notification.
4. Click **"Add Task"**.

### Breaking Down a Project

1. Enter a high-level project goal (e.g., "Plan summer vacation") in the task field.
2. Select a due date and time for the overall project.
3. Click the **"✨ Break Down"** button. The AI will generate sub-tasks and add them to the **"To Do"** column.

### Managing Tasks

- **Move:** Click and drag a task card from one column to another.
- **Edit:** Hover over a task and click the pencil icon.
- **Delete:** Hover over a task and click the trash can icon.

### Switching Views

- Use the **"Kanban"** and **"Calendar"** buttons to toggle between the two views at any time.

## 🛠️ Built With

- **HTML5**
- **Tailwind CSS** – For modern and responsive styling.
- **JavaScript (ES6+)** – For all application logic.
- **Gemini API** – For AI-powered task generation.
- **Canvas Confetti** – For the completion animation.

## Available to use at:
- Available at https://mikezhang69.github.io/task-manager/task-tracker.html, all tasks are stored locally in the browser you're currently using.

