"""Serialização centralizada de Task (elimina o mapeamento repetido nas rotas)."""


def task_to_dict(task):
    """Serialização completa e sanitizada (sem relacionamentos)."""
    return task.to_dict()


def task_with_overdue(task):
    """Serialização completa + flag ``overdue``."""
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    return data


def task_list_item(task):
    """Item da listagem ``GET /tasks`` (com nomes de usuário/categoria)."""
    data = task_with_overdue(task)
    data["user_name"] = task.user.name if task.user else None
    data["category_name"] = task.category.name if task.category else None
    return data


def task_summary(task):
    """Subconjunto usado em ``GET /users/<id>/tasks``."""
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "created_at": str(task.created_at),
        "due_date": str(task.due_date) if task.due_date else None,
        "overdue": task.is_overdue(),
    }
