"""Regras de negócio do domínio de tasks."""
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from services import serializers
from services.errors import NotFoundError, ValidationError
from services.notification_service import NotificationService
from services.time_utils import utcnow
from services.validators import (
    DEFAULT_PRIORITY,
    parse_due_date,
    parse_priority,
    validate_priority,
    validate_status,
    validate_title_length,
    validate_title_required,
)


def _serialize_tags(tags):
    if not tags:
        return None
    if isinstance(tags, list):
        return ",".join(tags)
    return tags


def list_tasks():
    tasks = (
        Task.query.options(joinedload(Task.user), joinedload(Task.category))
        .order_by(Task.id)
        .all()
    )
    return [serializers.task_list_item(t) for t in tasks]


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise NotFoundError("Task não encontrada")
    return serializers.task_with_overdue(task)


def create_task(data):
    title = data.get("title")
    validate_title_required(title)

    status = data.get("status", "pending")
    validate_status(status)

    priority = parse_priority(data.get("priority", DEFAULT_PRIORITY))
    validate_priority(priority)

    user_id = data.get("user_id")
    category_id = data.get("category_id")

    user = None
    if user_id:
        user = db.session.get(User, user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")
    if category_id and not db.session.get(Category, category_id):
        raise NotFoundError("Categoria não encontrada")

    task = Task(
        title=title,
        description=data.get("description", ""),
        status=status,
        priority=priority,
        user_id=user_id,
        category_id=category_id,
        due_date=parse_due_date(data.get("due_date")),
        tags=_serialize_tags(data.get("tags")),
    )

    db.session.add(task)
    db.session.commit()

    if user:
        NotificationService().notify_task_assigned(user, task)

    return serializers.task_to_dict(task)


def update_task(task_id, data):
    task = db.session.get(Task, task_id)
    if not task:
        raise NotFoundError("Task não encontrada")

    if "title" in data:
        validate_title_length(data["title"])
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "status" in data:
        validate_status(data["status"])
        task.status = data["status"]
    if "priority" in data:
        priority = parse_priority(data["priority"])
        validate_priority(priority)
        task.priority = priority
    if "user_id" in data:
        user_id = data["user_id"]
        if user_id and not db.session.get(User, user_id):
            raise NotFoundError("Usuário não encontrado")
        task.user_id = user_id
    if "category_id" in data:
        category_id = data["category_id"]
        if category_id and not db.session.get(Category, category_id):
            raise NotFoundError("Categoria não encontrada")
        task.category_id = category_id
    if "due_date" in data:
        task.due_date = parse_due_date(data["due_date"])
    if "tags" in data:
        task.tags = _serialize_tags(data["tags"])

    db.session.commit()
    return serializers.task_to_dict(task)


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise NotFoundError("Task não encontrada")
    db.session.delete(task)
    db.session.commit()
    return {"message": "Task deletada com sucesso"}


def search_tasks(query="", status="", priority="", user_id=""):
    q = Task.query

    if query:
        q = q.filter(
            or_(
                Task.title.like(f"%{query}%"),
                Task.description.like(f"%{query}%"),
            )
        )
    if status:
        q = q.filter(Task.status == status)
    if priority:
        priority = parse_priority(priority)
        q = q.filter(Task.priority == priority)
    if user_id:
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise ValidationError("Usuário inválido")
        q = q.filter(Task.user_id == user_id)

    return [serializers.task_to_dict(t) for t in q.order_by(Task.id).all()]


def task_stats():
    total = Task.query.count()

    status_counts = dict(
        db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all()
    )
    overdue = Task.query.filter(
        Task.due_date.isnot(None),
        Task.status.notin_(["done", "cancelled"]),
        Task.due_date < utcnow(),
    ).count()

    return {
        "total": total,
        "pending": status_counts.get("pending", 0),
        "in_progress": status_counts.get("in_progress", 0),
        "done": status_counts.get("done", 0),
        "cancelled": status_counts.get("cancelled", 0),
        "overdue": overdue,
        "completion_rate": round((status_counts.get("done", 0) / total) * 100, 2) if total > 0 else 0,
    }
