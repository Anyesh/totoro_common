from collections import defaultdict
from enum import StrEnum


class RoleEnum(StrEnum):
    OWNER = "owner"  # Super user
    ADMIN = "admin"  # 1 level below owner
    FAMILY = "family"  # verified + subscribed
    USER = "user"  # verified
    UNVERIFIED = "unverified"  # not verified
    BANNED = "banned"  # banned

    def all(self):
        return [
            RoleEnum.OWNER,
            RoleEnum.ADMIN,
            RoleEnum.FAMILY,
            RoleEnum.USER,
            RoleEnum.UNVERIFIED,
            RoleEnum.BANNED,
        ]


SCORE = {
    RoleEnum.BANNED: -1,
    RoleEnum.UNVERIFIED: 0,
    RoleEnum.USER: 1,
    RoleEnum.FAMILY: 2,
    RoleEnum.ADMIN: 3,
    RoleEnum.OWNER: 100,
}

ROLE_SCORE = defaultdict(lambda: 0, SCORE)
