*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Segoe UI', system-ui, sans-serif;
  background: #0f172a;
  color: #e2e8f0;
  min-height: 100vh;
  padding: 2rem 1rem;
}

.container {
  max-width: 720px;
  margin: 0 auto;
}

header {
  text-align: center;
  margin-bottom: 2rem;
}

header h1 {
  font-size: 2.4rem;
  font-weight: 700;
  background: linear-gradient(135deg, #38bdf8, #818cf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #94a3b8;
  margin-top: 0.4rem;
  font-size: 0.9rem;
}

.stats-bar {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.stats-bar span {
  background: #1e293b;
  padding: 0.4rem 1rem;
  border-radius: 999px;
  font-size: 0.85rem;
  color: #94a3b8;
}

.add-task, .task-list {
  background: #1e293b;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

h2 {
  font-size: 1.1rem;
  color: #cbd5e1;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

input[type="text"], textarea {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #e2e8f0;
  padding: 0.6rem 0.9rem;
  font-size: 0.95rem;
  resize: vertical;
  width: 100%;
}

input[type="text"]:focus, textarea:focus {
  outline: none;
  border-color: #38bdf8;
}

button[type="submit"] {
  align-self: flex-end;
  background: #38bdf8;
  color: #0f172a;
  border: none;
  border-radius: 8px;
  padding: 0.55rem 1.4rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

button[type="submit"]:hover { background: #7dd3fc; }

.task-item {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 10px;
  padding: 0.9rem 1rem;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  transition: border-color 0.2s;
}

.task-item:hover { border-color: #334155; }

.task-item.completed .task-title { text-decoration: line-through; color: #475569; }

.task-check {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #475569;
  cursor: pointer;
  flex-shrink: 0;
  margin-top: 2px;
  transition: background 0.2s, border-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.task-item.completed .task-check {
  background: #22c55e;
  border-color: #22c55e;
}

.task-check::after {
  content: '';
  display: block;
  width: 6px;
  height: 10px;
  border: 2px solid #0f172a;
  border-top: none;
  border-left: none;
  transform: rotate(45deg) translateY(-1px);
  opacity: 0;
}

.task-item.completed .task-check::after { opacity: 1; }

.task-body { flex: 1; }
.task-title { font-weight: 600; color: #e2e8f0; margin-bottom: 0.2rem; }
.task-desc { font-size: 0.85rem; color: #64748b; }
.task-date { font-size: 0.75rem; color: #334155; margin-top: 0.4rem; }

.task-delete {
  background: none;
  border: none;
  color: #475569;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
  padding: 2px 4px;
  border-radius: 4px;
  transition: color 0.2s;
}

.task-delete:hover { color: #ef4444; }

.loading { color: #475569; text-align: center; padding: 1rem; }

.badge {
  font-size: 0.7rem;
  background: #854d0e;
  color: #fef08a;
  padding: 2px 8px;
  border-radius: 999px;
  font-weight: 500;
}

.badge.hidden { display: none; }

.empty { color: #475569; text-align: center; padding: 1.5rem; font-size: 0.9rem; }
