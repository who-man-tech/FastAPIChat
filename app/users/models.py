from typing import Optional

from tortoise import fields
from tortoise.exceptions import DoesNotExist

from app.core.models import BaseDBModel
from app.users.schemes import UserCreateScheme
from app.users.services import UserService


class User(BaseDBModel):
    username = fields.CharField(max_length=20, unique=True, null=True)
    email = fields.CharField(max_length=255, unique=True)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    hashed_password = fields.CharField(max_length=128)
    is_superuser = fields.BooleanField(default=False)

    def full_name(self) -> str:
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.username

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        try:
            query = cls.get_or_none(email=email)
            user = await query
            return user
        except DoesNotExist:
            return None

    @classmethod
    async def get_by_username(cls, username: str) -> Optional["User"]:
        try:
            query = cls.get(username=username)
            user = await query
            return user
        except DoesNotExist:
            return None

    @classmethod
    async def create(cls, user_obj: UserCreateScheme) -> "User":
        user_dict = user_obj.dict()
        hashed_password = await UserService.hash_password(user_obj.password)
        user = cls(**user_dict, hashed_password=hashed_password)
        await user.save()
        return user

    class Meta:
        table = 'users'

    class PydanticMeta:
        computed = ["full_name"]
