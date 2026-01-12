from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, Task
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
# Allow both local development and production URLs
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    os.environ.get("FRONTEND_URL", "")
]
# Remove empty strings from allowed_origins
allowed_origins = [origin for origin in allowed_origins if origin]

CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# ==================== API ROUTES ====================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """READ: Get all tasks"""
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks]), 200

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """READ: Get a single task by ID"""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict()), 200

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """CREATE: Create a new task"""
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        completed=data.get('completed', False)
    )

    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """UPDATE: Update an existing task"""
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)

    db.session.commit()

    return jsonify(task.to_dict()), 200

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """DELETE: Delete a task"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully'}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Backend is running'}), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
