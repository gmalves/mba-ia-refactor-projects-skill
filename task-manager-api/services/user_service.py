"""Regras de negócio do domínio de usuários (incluindo autenticação)."""
from sqlalchemy.orm import joinedload

from database import db
from models.task import Task
from models.user import User
from services import serializers
from services.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from services.validators import (
    MIN_PASSWORD_LENGTH,
    validate_email_format,
    validate_role,
)


def list_users():
    users = User.query.options(joinedload(User.tasks)).order_by(User.id).all()
    result = []
    for user in users:
        data = user.to_dict()
        data["task_count"] = len(user.tasks)
        result.append(data)
    return result


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.id).all()
    data["tasks"] = [serializers.task_to_dict(t) for t in tasks]
    return data


def list_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.id).all()
    return [serializers.task_summary(t) for t in tasks]


def create_user(data):
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name:
        raise ValidationError("Nome é obrigatório")
    if not email:
        raise ValidationError("Email é obrigatório")
    if not password:
        raise ValidationError("Senha é obrigatória")
    validate_email_format(email)
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError("Senha deve ter no mínimo 4 caracteres")
    if User.query.filter_by(email=email).first():
        raise ConflictError("Email já cadastrado")
    validate_role(role)

    user = User(name=name, email=email, role=role)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    return user.to_dict()


def update_user(user_id, data):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")

    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        validate_email_format(data["email"])
        existing = User.query.filter_by(email=data["email"]).first()
        if existing and existing.id != user_id:
            raise ConflictError("Email já cadastrado")
        user.email = data["email"]
    if "password" in data:
        if len(data["password"]) < MIN_PASSWORD_LENGTH:
            raise ValidationError("Senha muito curta")
        user.set_password(data["password"])
    if "role" in data:
        validate_role(data["role"])
        user.role = data["role"]
    if "active" in data:
        if not isinstance(data["active"], bool):
            raise ValidationError("Active deve ser booleano")
        user.active = data["active"]

    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")

    # Exclui as tasks do usuário (transação única) para não deixar órfãs.
    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return {"message": "Usuário deletado com sucesso"}


def login(data):
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise ValidationError("Email e senha são obrigatórios")

    user = User.query.filter_by(email=email).first()
    if not user:
        raise UnauthorizedError("Credenciais inválidas")
    if not user.check_password(password):
        raise UnauthorizedError("Credenciais inválidas")
    if not user.active:
        raise ForbiddenError("Usuário inativo")

    return user
