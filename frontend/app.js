const API = '/api';

async function fetchStats() {
  try {
    const res = await fetch(`${API}/stats`);
    const data = await res.json();
    document.getElementById('stat-total').textContent = `Total: ${data.total}`;
    document.getElementById('stat-completed').textContent = `Done: ${data.completed}`;
    document.getElementById('stat-pending').textContent = `Pending: ${data.pending}`;
  } catch (e) {
    console.error('Stats fetch failed', e);
  }
}

async function fetchTasks() {
  const container = document.getElementById('tasks-container');
  const badge = document.getElementById('cache-badge');
  container.innerHTML = '<p class="loading">Loading...</p>';
  try {
    const res = await fetch(`${API}/tasks`);
    const data = await res.json();
    badge.classList.toggle('hidden', !data.cached);
    renderTasks(data.tasks, container);
  } catch (e) {
    container.innerHTML = '<p class="loading">Failed to load tasks.</p>';
  }
}

function renderTasks(tasks, container) {
  if (!tasks.length) {
    container.innerHTML = '<p class="empty">No tasks yet - add one above.</p>';
    return;
  }
  container.innerHTML = tasks.map(t => `
    <div class="task-item ${t.completed ? 'completed' : ''}" data-id="${t.id}">
      <div class="task-check" onclick="toggleTask(${t.id}, ${!t.completed})"></div>
      <div class="task-body">
        <div class="task-title">${escHtml(t.title)}</div>
        ${t.description ? `<div class="task-desc">${escHtml(t.description)}</div>` : ''}
        <div class="task-date">${new Date(t.created_at).toLocaleString()}</div>
      </div>
      <button class="task-delete" onclick="deleteTask(${t.id})" title="Delete">&#x2715;</button>
    </div>
  `).join('');
}

async function toggleTask(id, completed) {
  await fetch(`${API}/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed }),
  });
  refresh();
}

async function deleteTask(id) {
  await fetch(`${API}/tasks/${id}`, { method: 'DELETE' });
  refresh();
}

function refresh() { fetchTasks(); fetchStats(); }

document.getElementById('task-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = document.getElementById('task-title').value.trim();
  const description = document.getElementById('task-desc').value.trim();
  if (!title) return;
  await fetch(`${API}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, description }),
  });
  e.target.reset();
  refresh();
});

function escHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

refresh();
