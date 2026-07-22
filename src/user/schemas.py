from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .enums import AccountStatus, BasicRole, RelationStatus, RelationType, StudentSort

# fmt: off
# ==== Схемы для взаимодействия с личной информацией пользователя ====


class UserRead(BaseModel):
    id:                    int
    user_id:               UUID | None
    basic_role:            BasicRole
    account_status:        AccountStatus
    email:                 str
    first_name:            str | None       = None
    last_name:             str | None       = None
    middle_name:           str | None       = None
    nickname:              str | None       = None
    avatar_url:            str | None       = None
    date_of_birth:         date | None      = None
    contacts:              dict | None      = None
    messengers:            dict | None      = None
    timezone:              str
    locale:                str
    bio:                   str | None       = None
    created_at:            datetime
    updated_at:            datetime
    version:               int

    model_config = {"from_attributes": True}


class DeleteProfileRequest(BaseModel):
    access_token:          str


class ReadProfileRequest(BaseModel):
    access_token:          str


class UserUpdate(BaseModel):
    version:               int
    first_name:            str | None       = Field(default=None, max_length=100)
    last_name:             str | None       = Field(default=None, max_length=100)
    middle_name:           str | None       = Field(default=None, max_length=100)
    nickname:              str | None       = Field(default=None, max_length=200)
    avatar_url:            str | None       = Field(default=None, max_length=512)
    date_of_birth:         date | None      = None
    contacts:              dict | None      = None
    messengers:            dict | None      = None
    timezone:              str | None       = Field(default=None, max_length=64)
    locale:                str | None       = Field(default=None, max_length=16)
    bio:                   str | None       = None
    basic_role:            BasicRole | None = None


class UserUpdateRequest(UserUpdate):
    access_token:          str


# ==== Схемы для взаимодействия с учениками ====


class StudentCreate(BaseModel):
    first_name:            str | None  = Field(default=None, max_length=100)
    last_name:             str | None  = Field(default=None, max_length=100)
    middle_name:           str | None  = Field(default=None, max_length=100)
    nickname:              str | None  = Field(default=None, max_length=200)
    date_of_birth:         date | None = None
    contacts:              dict | None = None
    messengers:            dict | None = None
    timezone:              str         = Field(default="UTC", max_length=64)
    locale:                str         = Field(default="ru", max_length=16)
    subjects:              list | None = None
    level:                 str | None  = Field(default=None, max_length=100)
    notes:                 str | None  = None
    tags:                  list | None = None


class StudentCreateRequest(StudentCreate):
    access_token:          str


class RelationRead(BaseModel):
    id:                    int
    from_user_id:          int
    to_user_id:            int
    relation_type:         RelationType
    subjects:              list | None    = None
    level:                 str | None     = None
    status:                RelationStatus
    notes:                 str | None     = None
    tags:                  list | None    = None
    parent_rights:         dict | None    = None
    start_date:            date | None    = None
    end_date:              date | None    = None
    created_at:            datetime
    updated_at:            datetime
    version:               int

    model_config = {"from_attributes": True}


class ListStudents(BaseModel):
    offset:                int                   = Field(default=0, ge=0)
    limit:                 int                   = Field(default=10, ge=1, le=200)
    status:                RelationStatus | None = None
    subject:               str | None            = None
    tag:                   str | None            = None
    group_row:             int | None            = None
    search:                str | None            = None
    sort:                  StudentSort           = StudentSort.created
    descending:            bool                  = True


class ListStudentsRequest(ListStudents):
    access_token:          str


class StudentListItem(BaseModel):
    relation:              RelationRead
    student:               UserRead

# fmt: on
