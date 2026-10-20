"""Regras de negócio do domínio de categorias."""
from sqlalchemy import func

from database import db
from models.category import Category
from models.task import Task
from services.errors import NotFoundError, ValidationError
from services.validators import DEFAULT_COLOR


def list_categories():
    categories = Category.query.order_by(Category.id).all()
    counts = dict(
        db.session.query(Task.category_id, func.count(Task.id))
        .filter(Task.category_id.isnot(None))
        .group_by(Task.category_id)
        .all()
    )
    result = []
    for category in categories:
        data = category.to_dict()
        data["task_count"] = counts.get(category.id, 0)
        result.append(data)
    return result


def create_category(data):
    name = data.get("name")
    if not name:
        raise ValidationError("Nome é obrigatório")

    category = Category(
        name=name,
        description=data.get("description", ""),
        color=data.get("color", DEFAULT_COLOR),
    )
    db.session.add(category)
    db.session.commit()
    return category.to_dict()


def update_category(cat_id, data):
    category = db.session.get(Category, cat_id)
    if not category:
        raise NotFoundError("Categoria não encontrada")

    if "name" in data:
        category.name = data["name"]
    if "description" in data:
        category.description = data["description"]
    if "color" in data:
        category.color = data["color"]

    db.session.commit()
    return category.to_dict()


def delete_category(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        raise NotFoundError("Categoria não encontrada")

    # Desassocia as tasks antes de excluir (transação única; evita órfãs).
    for task in Task.query.filter_by(category_id=cat_id).all():
        task.category_id = None
    db.session.delete(category)
    db.session.commit()
    return {"message": "Categoria deletada"}
