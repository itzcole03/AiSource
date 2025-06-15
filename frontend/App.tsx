import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Import all components
import AgentStatusDashboard from './components/AgentStatusDashboard.tsx';import SystemLogsViewer from './components/SystemLogsViewer.tsx';import TaskCreationForm from './components/TaskCreationForm.tsx';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Ultimate Copilot Dashboard</h1>
          <nav>
            <Link to="/" className="nav-link">Agent Status</Link>
            <Link to="/tasks" className="nav-link">Task Management</Link>
            <Link to="/logs" className="nav-link">System Logs</Link>
          </nav>
        </header>
        
        <main className="App-main">
          <Routes>
            <Route path="/" element={<AgentStatusDashboard />} />
            <Route path="/tasks" element={<TaskCreationForm />} />
            <Route path="/logs" element={<SystemLogsViewer />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
