from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import uuid

app = Flask(__name__, static_folder="../frontend")

# In-memory task store (replace with DB for production)
tasks = {}

# Task model example:
# {
#   "id": "uuid",
#   "title": "Task title",
#   "due_date": "YYYY-MM-DD",
#   "due_time": "HH:MM",
#   "reminder": true,
#   "status": "todo" | "inprogress" | "done"
# }

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(list(tasks.values()))

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.json
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "title": data.get("title"),
        "due_date": data.get("due_date"),
        "due_time": data.get("due_time"),
        "reminder": data.get("reminder", False),
        "status": data.get("status", "todo")
    }
    tasks[task_id] = task
    return jsonify(task), 201

@app.route("/api/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    if task_id not in tasks:
        return jsonify({"error": "Task not found"}), 404
    data = request.json
    for key in ["title", "due_date", "due_time", "reminder", "status"]:
        if key in data:
            tasks[task_id][key] = data[key]
    return jsonify(tasks[task_id])

@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    if task_id in tasks:
        del tasks[task_id]
        return "", 204
    return jsonify({"error": "Task not found"}), 404

@app.route("/api/ai/breakdown", methods=["POST"])
def ai_breakdown():
    # Stub: Integrate Gemini API here
    data = request.json
    project_title = data.get("title")
    # Return dummy subtasks for now
    subtasks = [
        {"title": f"Subtask {i+1} for {project_title}", "status": "todo"} for i in range(3)
    ]
    return jsonify(subtasks)

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(debug=True)
