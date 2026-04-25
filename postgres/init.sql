CREATE TABLE IF NOT EXISTS tasks (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    completed   BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO tasks (title, description) VALUES
    ('Set up Docker Compose', 'Multi-service orchestration with Compose v2'),
    ('Wire up Redis cache', 'Cache GET /api/tasks for 60 seconds')
ON CONFLICT DO NOTHING;
