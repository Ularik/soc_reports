from ninja import Schema
from typing import Optional


class UserCreateSchema(Schema):
    username: str
    password: str
    is_staff: bool
