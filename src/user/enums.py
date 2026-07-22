from enum import StrEnum, auto


# fmt: off
class BasicRole(StrEnum):
    """Роль для главного экрана фронта"""

    tutor     = auto()
    student   = auto()


class AccountStatus(StrEnum):
    """Статус аккаунта человека в жизненном цикле гибридного ученика"""

    managed   = auto()
    """карточка без аккаунта, заведена репетитором"""
    invited   = auto()
    """приглашение отправлено"""
    active    = auto()
    """есть полноценный аккаунт"""
    blocked   = auto()
    """заблокирован"""
    deleted   = auto()
    """soft-delete"""


class RelationType(StrEnum):
    """Тип связи между людьми"""

    tutor_of  = auto()
    parent_of = auto()


class RelationStatus(StrEnum):
    active    = auto()
    paused    = auto()
    archived  = auto()


class StudentSort(StrEnum):
    name_     = auto()
    created   = auto()


# fmt: on
