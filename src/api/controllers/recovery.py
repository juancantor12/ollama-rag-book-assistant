"""Recovery code controller."""

from datetime import datetime, timedelta
import secrets
from typing import Tuple
from passlib.context import CryptContext
from api.db import Database
from api.models.recovery_code import RecoveryCode
from api.models.user import User
from app.utils import Utils


class RecoveryController:
    """Controller for recovery code flow."""

    def __init__(self):
        self.db = Database()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def generate_code(self) -> str:
        """Generate a fresh recovery code and persist its hash."""
        if not self.db.table_exists(RecoveryCode.__tablename__):
            Utils.logger.warning(
                "Recovery codes table missing. Run /admin/create_db_tables first."
            )
            return ""

        now = datetime.utcnow()
        code = f"{secrets.randbelow(10**6):06d}"
        code_hash = self.pwd_context.hash(code)
        expires_at = now + timedelta(minutes=Utils.API_RECOVERY_CODE_EXPIRE_MINUTES)

        # Invalidate any unused codes so only one is active at a time.
        (
            self.db.session.query(RecoveryCode)
            .filter(RecoveryCode.used.is_(False))
            .update({"used": True})
        )
        self.db.session.add(
            RecoveryCode(
                code_hash=code_hash,
                created_at=now,
                expires_at=expires_at,
                used=False,
            )
        )
        self.db.session.commit()
        return code

    def reset_password(
        self, username: str, new_password: str, recovery_code: str
    ) -> Tuple[bool, str]:
        """Reset an admin password if the recovery code is valid."""
        if not self.db.table_exists(RecoveryCode.__tablename__):
            return False, "missing_table"

        now = datetime.utcnow()
        code_record = (
            self.db.session.query(RecoveryCode)
            .filter(
                RecoveryCode.used.is_(False),
                RecoveryCode.expires_at > now,
            )
            .order_by(RecoveryCode.created_at.desc())
            .first()
        )
        if not code_record or not self.pwd_context.verify(
            recovery_code, code_record.code_hash
        ):
            return False, "invalid_code"

        user = (
            self.db.session.query(User).filter(User.username == username).first()
        )
        if not user:
            return False, "user_not_found"

        if "manage_access" not in user.role.get_role_permissions():
            return False, "not_admin"

        user.password = self.pwd_context.hash(new_password)
        code_record.used = True
        self.db.session.commit()
        return True, "ok"
