import hashlib
import re

from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from services.time_utils import utcnow


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        # O campo "password" é intencionalmente omitido (nunca exposto em resposta).
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
            "created_at": str(self.created_at),
        }

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd, method="pbkdf2:sha256")

    def check_password(self, pwd):
        """Valida a senha; migra silenciosamente hashes legados (MD5/texto puro)."""
        if self._is_legacy_hash() and self._matches_legacy(pwd):
            self.password = generate_password_hash(pwd, method="pbkdf2:sha256")
            db.session.commit()
            return True
        return check_password_hash(self.password, pwd)

    def _is_legacy_hash(self):
        return bool(re.match(r"^[a-f0-9]{32}$", self.password or ""))

    def _matches_legacy(self, pwd):
        return self.password == pwd or self.password == hashlib.md5(pwd.encode()).hexdigest()

    def is_admin(self):
        return self.role == "admin"
