import React, { useState, useEffect } from 'react';
import { taskAPI } from './services/api';
import TaskForm from './components/TaskForm';
import TaskList from './components/TaskList';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch tasks on component mount
  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await taskAPI.getAllTasks();
      setTasks(data);
    } catch (err) {
      setError('Failed to fetch tasks. Is the backend running?');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (taskData) => {
    try {
      const newTask = await taskAPI.createTask(taskData);
      setTasks([newTask, ...tasks]);
    } catch (err) {
      alert('Failed to create task');
      console.error('Error creating task:', err);
    }
  };

  const handleUpdateTask = async (id, taskData) => {
    try {
      const updatedTask = await taskAPI.updateTask(id, taskData);
      setTasks(tasks.map((task) => (task.id === id ? updatedTask : task)));
    } catch (err) {
      alert('Failed to update task');
      console.error('Error updating task:', err);
    }
  };

  const handleDeleteTask = async (id) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await taskAPI.deleteTask(id);
      setTasks(tasks.filter((task) => task.id !== id));
    } catch (err) {
      alert('Failed to delete task');
      console.error('Error deleting task:', err);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Task Manager</h1>
        <p>A simple CRUD application with Flask + React</p>
      </header>

      <main className="app-main">
        <TaskForm onSubmit={handleCreateTask} />

        {loading && <div className="loading">Loading tasks...</div>}
        {error && <div className="error">{error}</div>}
        {!loading && !error && (
          <TaskList
            tasks={tasks}
            onUpdate={handleUpdateTask}
            onDelete={handleDeleteTask}
          />
        )}
      </main>
    </div>
  );
}

export default App;
