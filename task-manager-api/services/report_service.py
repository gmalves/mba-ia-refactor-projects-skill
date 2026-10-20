"""Regras de negócio dos relatórios (agregações sem N+1)."""
from datetime import timedelta

from sqlalchemy import case, func

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from services.errors import NotFoundError
from services.time_utils import utcnow


def summary_report():
    now = utcnow()
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    status_counts = dict(
        db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
    )
    priority_counts = dict(
        db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
    )

    overdue_tasks = Task.query.filter(
        Task.due_date.isnot(None),
        Task.status.notin_(["done", "cancelled"]),
        Task.due_date < now,
    ).all()
    overdue_list = [
        {
            "id": t.id,
            "title": t.title,
            "due_date": str(t.due_date),
            "days_overdue": (now - t.due_date).days,
        }
        for t in overdue_tasks
    ]

    seven_days_ago = now - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == "done", Task.updated_at >= seven_days_ago
    ).count()

    user_rows = (
        db.session.query(
            Task.user_id,
            func.count(Task.id),
            func.sum(case((Task.status == "done", 1), else_=0)),
        )
        .filter(Task.user_id.isnot(None))
        .group_by(Task.user_id)
        .all()
    )
    user_counts = {user_id: (total, completed) for user_id, total, completed in user_rows}

    user_stats = []
    for user in User.query.order_by(User.id).all():
        total, completed = user_counts.get(user.id, (0, 0))
        completed = completed or 0
        user_stats.append(
            {
                "user_id": user.id,
                "user_name": user.name,
                "total_tasks": total,
                "completed_tasks": completed,
                "completion_rate": round((completed / total) * 100, 2) if total > 0 else 0,
            }
        )

    return {
        "generated_at": str(now),
        "overview": {
            "total_tasks": total_tasks,
            "total_users": total_users,
            "total_categories": total_categories,
        },
        "tasks_by_status": {
            "pending": status_counts.get("pending", 0),
            "in_progress": status_counts.get("in_progress", 0),
            "done": status_counts.get("done", 0),
            "cancelled": status_counts.get("cancelled", 0),
        },
        "tasks_by_priority": {
            "critical": priority_counts.get(1, 0),
            "high": priority_counts.get(2, 0),
            "medium": priority_counts.get(3, 0),
            "low": priority_counts.get(4, 0),
            "minimal": priority_counts.get(5, 0),
        },
        "overdue": {
            "count": len(overdue_list),
            "tasks": overdue_list,
        },
        "recent_activity": {
            "tasks_created_last_7_days": recent_tasks,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")

    tasks = Task.query.filter_by(user_id=user_id).all()

    done = pending = in_progress = cancelled = overdue = high_priority = 0
    for task in tasks:
        if task.status == "done":
            done += 1
        elif task.status == "pending":
            pending += 1
        elif task.status == "in_progress":
            in_progress += 1
        elif task.status == "cancelled":
            cancelled += 1

        if task.priority <= 2:
            high_priority += 1

        if task.is_overdue():
            overdue += 1

    total = len(tasks)
    return {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "statistics": {
            "total_tasks": total,
            "done": done,
            "pending": pending,
            "in_progress": in_progress,
            "cancelled": cancelled,
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
        },
    }
