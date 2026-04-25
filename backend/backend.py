from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import redis
import os
import json
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql://appuser:apppassword@postgres:5432/appdb"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    decode_responses=True,
)

CACHE_TTL = 60


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
        }


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "backend"})


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    cached = redis_client.get("tasks:all")
    if cached:
        return jsonify({"tasks": json.loads(cached), "cached": True})
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    result = [t.to_dict() for t in tasks]
    redis_client.setex("tasks:all", CACHE_TTL, json.dumps(result))
    return jsonify({"tasks": result, "cached": False})


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400
    task = Task(title=data["title"], description=data.get("description", ""))
    db.session.add(task)
    db.session.commit()
    redis_client.delete("tasks:all")
    return jsonify(task.to_dict()), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "completed" in data:
        task.completed = data["completed"]
    db.session.commit()
    redis_client.delete("tasks:all")
    return jsonify(task.to_dict())


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    redis_client.delete("tasks:all")
    return jsonify({"message": "deleted"})


@app.route("/api/stats")
def stats():
    total = Task.query.count()
    completed = Task.query.filter_by(completed=True).count()
    return jsonify({"total": total, "completed": completed, "pending": total - completed})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=False)
