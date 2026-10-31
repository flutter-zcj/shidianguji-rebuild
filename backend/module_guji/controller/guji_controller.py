from typing import Annotated

from fastapi import Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_session import DBSessionDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel, DynamicResponseModel, PageResponseModel
from module_guji.entity.vo.guji_vo import (
    GujiAudioModel,
    GujiBookModel,
    GujiBookPageQueryModel,
    GujiBookshelfAddModel,
    GujiBookshelfModel,
    GujiChapterModel,
    GujiHistoryModel,
    GujiParagraphPageQueryModel,
    GujiReadHistoryModel,
)
from module_guji.service.guji_service import GujiService
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.response_util import ResponseUtil

# 公开接口（无需登录）：书目浏览、章节与段落阅读、音频列表
_guji_public_routes = [
    {'path': '/guji/book/page', 'methods': ['GET']},
    {'path': '/guji/book/{book_id}', 'methods': ['GET']},
    {'path': '/guji/book/{book_id}/chapters', 'methods': ['GET']},
    {'path': '/guji/chapter/{chapter_id}/paragraphs', 'methods': ['GET']},
    {'path': '/guji/audio/{book_id}', 'methods': ['GET']},
]

guji_controller = APIRouterPro(
    prefix='/guji', order_num=20, tags=['古籍阅读平台'], dependencies=[PreAuthDependency(_guji_public_routes)]
)


@guji_controller.get(
    '/book/page',
    summary='古籍书目分页列表',
    description='支持按书名模糊、分类、朝代筛选',
    response_model=DynamicResponseModel[PageResponseModel[GujiBookModel]],
)
async def get_book_page(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    page_num: Annotated[int, Query(ge=1, description='当前页码')] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description='每页记录数')] = 10,
    book_name: Annotated[str | None, Query(description='书名（模糊查询）')] = None,
    category: Annotated[str | None, Query(description='分类（经/史/子/集/蒙学）')] = None,
    dynasty: Annotated[str | None, Query(description='朝代')] = None,
) -> Response:
    result = await GujiService.get_book_list_services(
        query_db,
        GujiBookPageQueryModel(
            bookName=book_name, category=category, dynasty=dynasty, pageNum=page_num, pageSize=page_size
        ),
    )
    return ResponseUtil.success(data=result)


@guji_controller.get(
    '/book/{book_id}',
    summary='古籍书目详情',
    response_model=DataResponseModel[GujiBookModel],
)
async def get_book_detail(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    book_id: Annotated[int, Path(description='书目ID')],
) -> Response:
    result = await GujiService.get_book_detail_services(query_db, book_id)
    return ResponseUtil.success(data=result)


@guji_controller.get(
    '/book/{book_id}/chapters',
    summary='章节目录',
    response_model=DataResponseModel[list[GujiChapterModel]],
)
async def get_book_chapters(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    book_id: Annotated[int, Path(description='书目ID')],
) -> Response:
    result = await GujiService.get_chapter_list_services(query_db, book_id)
    return ResponseUtil.success(data=result)


@guji_controller.get(
    '/chapter/{chapter_id}/paragraphs',
    summary='章节段落分页',
    description='模拟原版段落分页接口语义，支持按页码加载',
    response_model=DynamicResponseModel[PageResponseModel[dict]],
)
async def get_chapter_paragraphs(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    chapter_id: Annotated[int, Path(description='章节ID')],
    page_num: Annotated[int, Query(ge=1, description='当前页码')] = 1,
    page_size: Annotated[int, Query(ge=1, le=200, description='每页记录数')] = 20,
) -> Response:
    result = await GujiService.get_paragraph_page_services(
        query_db,
        GujiParagraphPageQueryModel(chapterId=chapter_id, pageNum=page_num, pageSize=page_size),
    )
    return ResponseUtil.success(data=result)


@guji_controller.get(
    '/bookshelf',
    summary='我的书架',
    description='需登录，返回书架书目与最近阅读进度',
    response_model=DataResponseModel[list[GujiBookshelfModel]],
)
async def get_bookshelf(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await GujiService.get_bookshelf_list_services(query_db, current_user.user.user_id)
    return ResponseUtil.success(data=result)


@guji_controller.post(
    '/bookshelf',
    summary='加入书架',
    description='需登录',
    response_model=DataResponseModel,
)
async def add_bookshelf(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    add_object: GujiBookshelfAddModel,
) -> Response:
    result = await GujiService.add_bookshelf_services(query_db, current_user.user.user_id, add_object)
    return ResponseUtil.success(data=result)


@guji_controller.delete(
    '/bookshelf/{book_id}',
    summary='移出书架',
    description='需登录',
    response_model=DataResponseModel,
)
async def delete_bookshelf(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    book_id: Annotated[int, Path(description='书目ID')],
) -> Response:
    result = await GujiService.delete_bookshelf_services(query_db, current_user.user.user_id, book_id)
    return ResponseUtil.success(data=result)


@guji_controller.get(
    '/history',
    summary='阅读历史',
    description='需登录，按时间倒序返回最近50条',
    response_model=DataResponseModel[list[GujiHistoryModel]],
)
async def get_history(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await GujiService.get_history_list_services(query_db, current_user.user.user_id)
    return ResponseUtil.success(data=result)


@guji_controller.post(
    '/history',
    summary='上报阅读进度',
    description='需登录，写入阅读历史并同步书架进度',
    response_model=DataResponseModel,
)
async def add_history(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    history_object: GujiReadHistoryModel,
) -> Response:
    result = await GujiService.add_history_services(query_db, current_user.user.user_id, history_object)
    return ResponseUtil.success(data=result)


@guji_controller.get(
    '/audio/{book_id}',
    summary='听书音频列表',
    description='返回书目下全部音频（章节级/全书级）',
    response_model=DataResponseModel[list[GujiAudioModel]],
)
async def get_audio_list(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    book_id: Annotated[int, Path(description='书目ID')],
) -> Response:
    result = await GujiService.get_audio_list_services(query_db, book_id)
    return ResponseUtil.success(data=result)
