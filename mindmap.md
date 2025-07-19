
# 🧠 Task Tracker Project Mind Map

## 🎯 Central Idea

**Kanban & Calendar Task Tracker**

---

## I. Core Functionality

### A. Task Management (CRUD)
- **Create:** Add new tasks with title, due date, time, and reminder option.
- **Read:** View tasks in multiple formats.
- **Update:** Edit all task details in a pop-up modal.
- **Delete:** Remove tasks with a confirmation step.

### B. Persistence
- **Local Storage:** Saves all tasks in the browser.
- **Auto-Save:** State is saved after any change (add, edit, delete, move).
- **Auto-Load:** Tasks are automatically loaded when the app starts.

### C. State Management
- **Tasks Array:** A single source of truth for all task data.
- **View State:** Tracks whether the user is on the Kanban or Calendar view.

---

## II. UI/UX (User Interface & Experience)

### A. Main Views
- **Kanban Board:** Visual workflow management.
  - Columns: To Do, In Progress, Done
  - Drag & Drop: Intuitive task status updates
  - Sorting: Tasks are chronologically sorted by date and time
- **Calendar View:** Date-focused scheduling.
  - Monthly Layout: Clear overview of deadlines
  - Task Display: Tasks shown on their due dates, color-coded by status
  - Navigation: Easily switch between months

### B. User Input & Forms
- **Task Creation Form:** Fields for text, date, and time
- **Edit Modal:** A pop-up form to update existing tasks
- **Input Validation:** Ensures tasks have a title and due date before enabling the "Add" button

### C. User Feedback
- **Confetti Animation:** A visual reward for completing a task
- **Error Modals:** Clearly communicates issues (e.g., API errors)
- **Loading Indicators:** A spinner shows when the AI is working

---

## III. Advanced Features

### A. Gemini AI Integration
- **Task Breakdown:** User provides a high-level goal
- **API Call:** Sends the prompt to the Gemini API
- **JSON Parsing:** Processes the AI's response to create multiple sub-tasks

### B. Reminder System
- **Notification Opt-In:** User can check a box to set a reminder
- **Browser Permissions:** Asks the user for permission to show notifications
- **Background Timer:** A setInterval function checks for upcoming tasks every 30 seconds
- **Notification Trigger:** Sends a desktop notification 15 minutes before the task's due time

---

## IV. Technology Stack

### A. Frontend
- **HTML5:** The core structure of the application
- **JavaScript (ES6+):** Handles all logic, state, and interactions

### B. Styling
- **Tailwind CSS:** For a modern, utility-first approach to design

### C. Libraries & APIs
- **Gemini API:** For artificial intelligence capabilities
- **Canvas Confetti:** For the celebratory animation
- **Web APIs:** Utilizes standard browser APIs for Notifications and Local Storage