from fastapi import APIRouter, Depends, Query, Response, status

from src.auth.dependency import get_access_token
from src.auth.utils import clear_auth_cookies
from src.rabbit import RabbitRPCResponse, rpc_handler
from src.schemas import Page

from .schemas import (
    DeleteProfileRequest,
    ListStudents,
    ListStudentsRequest,
    ReadProfileRequest,
    RelationRead,
    StudentCreate,
    StudentCreateRequest,
    StudentListItem,
    UserRead,
    UserUpdate,
    UserUpdateRequest,
)

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/me")
async def get_me(access_token: str = Depends(get_access_token)) -> UserRead:
    """Получить пользователя на основе данных access_token"""

    return await rpc_handler(
        ReadProfileRequest(access_token=access_token),
        "GET-user_service/profile/me",
        RabbitRPCResponse[UserRead],
        "User service",
        timeout=10,
        data_expected=True,
    )


@user_router.put("/me")
async def update_me(user: UserUpdate, access_token: str = Depends(get_access_token)) -> UserRead:
    """Получить пользователя на основе данных access_token"""

    return await rpc_handler(
        UserUpdateRequest(access_token=access_token, **user.model_dump(exclude_unset=True)),
        "PUT-user_service/profile/me",
        RabbitRPCResponse[UserRead],
        "User service",
        timeout=10,
        data_expected=True,
    )


@user_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    response: Response,
    access_token: str = Depends(get_access_token),
) -> None:
    """Получить пользователя на основе данных access_token"""

    await rpc_handler(
        DeleteProfileRequest(access_token=access_token),
        "DELETE-user_service/profile/me",
        RabbitRPCResponse,
        "User service",
        timeout=10,
        data_expected=False,
    )

    clear_auth_cookies(response)


student_router = APIRouter(prefix="/student", tags=["student"])


@student_router.post("")
async def create_student(
    student: StudentCreate,
    access_token: str = Depends(get_access_token),
) -> RelationRead:
    """Создать управляемую карточку ученика + связь tutor_of одной операцией"""

    return await rpc_handler(
        StudentCreateRequest(access_token=access_token, **student.model_dump(exclude_unset=True)),
        "POST-user_service/student",
        RabbitRPCResponse[RelationRead],
        "User service",
        timeout=10,
        data_expected=True,
    )


@student_router.get("")
async def get_students(
    params: ListStudents = Query(),
    access_token: str = Depends(get_access_token),
) -> Page[StudentListItem]:
    """Список своих учеников с фильтрами/поиском/сортировкой"""

    return await rpc_handler(
        ListStudentsRequest(access_token=access_token, **params.model_dump(exclude_unset=True)),
        "GET-user_service/student",
        RabbitRPCResponse[Page[StudentListItem]],
        "User service",
        timeout=10,
        data_expected=True,
    )
