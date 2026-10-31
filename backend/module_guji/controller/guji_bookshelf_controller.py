"""
识典古籍模块 - 书架控制器

对应原App的 /api/ancientlib/read/bookshelf/* 系列接口（V1/V3/V4 三套并存）。
"""

from typing import Annotated, Any

from fastapi import Body, Request, Response

from common.router import APIRouterPro
from module_guji.aspect.guji_auth import CurrentGujiUserDependency, GujiUserModel
from module_guji.aspect.guji_session import GujiDbSession
from module_guji.service.guji_user_service import GujiShelfService
from utils.response_util import ResponseUtil

bookshelf_controller = APIRouterPro(prefix='/api/ancientlib/read/bookshelf', order_num=210, tags=['识典古籍-书架'])

_DEFAULT_TYPE = 'book'


def _page(body: dict[str, Any]) -> tuple[int, int]:
    """
    从请求体中解析分页参数

    :param body: 请求体
    :return: 页码与每页条数
    """
    try:
        page_num = int(body.get('pageNum') or 1)
    except (TypeError, ValueError):
        page_num = 1
    try:
        page_size = int(body.get('pageSize') or 20)
    except (TypeError, ValueError):
        page_size = 20
    return page_num, page_size


@bookshelf_controller.post('/list/', summary='获取书架列表V1', description='兼容旧版书架列表')
async def guji_shelf_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    page_num, page_size = _page(body)
    result = await GujiShelfService.list_shelf_services(
        query_db, current_user.user_id, body.get('shelfBizType') or _DEFAULT_TYPE, page_num, page_size
    )
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/list/v2', summary='获取书架列表V2', description='兼容旧版书架列表（V2）')
async def guji_shelf_list_v2(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    page_num, page_size = _page(body)
    result = await GujiShelfService.list_shelf_services(
        query_db, current_user.user_id, body.get('shelfBizType') or _DEFAULT_TYPE, page_num, page_size
    )
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/list-all/', summary='获取全部书架书籍V1', description='书架页全量拉取')
async def guji_shelf_list_all(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    page_num, page_size = _page(body)
    result = await GujiShelfService.list_shelf_services(
        query_db, current_user.user_id, body.get('shelfBizType') or _DEFAULT_TYPE, page_num, page_size
    )
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/list-all/v3/', summary='获取全部书架书籍V3', description='书架页全量拉取（V3）')
async def guji_shelf_list_all_v3(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    page_num, page_size = _page(body)
    result = await GujiShelfService.list_shelf_services(
        query_db, current_user.user_id, body.get('shelfBizType') or _DEFAULT_TYPE, page_num, page_size
    )
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/list-all/v4/', summary='获取全部书架书籍V4', description='书架页全量拉取（V4，当前版本）')
async def guji_shelf_list_all_v4(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    page_num, page_size = _page(body)
    result = await GujiShelfService.list_shelf_services(
        query_db, current_user.user_id, body.get('shelfBizType') or _DEFAULT_TYPE, page_num, page_size
    )
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/add/', summary='加入书架', description='书籍详情/阅读器加入书架')
async def guji_shelf_add(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.mutate_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='已加入书架')


@bookshelf_controller.post('/batch-add/', summary='批量加入书架', description='书单页批量加入书架')
async def guji_shelf_batch_add(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.mutate_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='已加入书架')


@bookshelf_controller.post('/batch-add/v3/', summary='批量加入书架V3', description='书架批量操作（V3）')
async def guji_shelf_batch_add_v3(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.mutate_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='已加入书架')


@bookshelf_controller.post('/batch-add/v4/', summary='批量加入书架V4', description='书架批量操作（V4）')
async def guji_shelf_batch_add_v4(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.mutate_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='已加入书架')


@bookshelf_controller.post('/delete/', summary='移出书架', description='书籍详情/阅读器移出书架')
async def guji_shelf_delete(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.delete_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='已移出书架')


@bookshelf_controller.post('/batch-delete/v3/', summary='批量移出书架V3', description='书架批量删除（V3）')
async def guji_shelf_batch_delete_v3(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.delete_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='已移出书架')


@bookshelf_controller.post('/batch-delete/v4/', summary='批量移出书架V4', description='书架批量删除（V4）')
async def guji_shelf_batch_delete_v4(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.delete_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='已移出书架')


@bookshelf_controller.post('/update/', summary='更新书架信息', description='更新阅读进度、分组')
async def guji_shelf_update(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.mutate_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/batch-update/v3/', summary='批量更新书架V3', description='书架批量更新（V3）')
async def guji_shelf_batch_update_v3(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.mutate_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/batch-update/v4/', summary='批量更新书架V4', description='书架批量更新（V4）')
async def guji_shelf_batch_update_v4(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.mutate_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/check/', summary='查询是否在书架', description='书籍详情判断是否已收藏')
async def guji_shelf_check(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.check_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/batch-check/', summary='批量查询是否在书架', description='列表页批量判断书架状态')
async def guji_shelf_batch_check(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.check_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/batch-check/v3/', summary='批量查询书架状态V3', description='列表页批量判断书架状态（V3）')
async def guji_shelf_batch_check_v3(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.check_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/batch-check/v4/', summary='批量查询书架状态V4', description='列表页批量判断书架状态（V4）')
async def guji_shelf_batch_check_v4(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiShelfService.check_shelf_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/batch-get/v3/', summary='批量获取书架详情V3', description='书架书籍详情补充（V3）')
async def guji_shelf_batch_get_v3(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiShelfService.check_shelf_services(query_db, current_user.user_id, body)
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/batch-get/v4/', summary='批量获取书架详情V4', description='书架书籍详情补充（V4）')
async def guji_shelf_batch_get_v4(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiShelfService.check_shelf_services(query_db, current_user.user_id, body)
    return ResponseUtil.success(data=result)


@bookshelf_controller.post('/book-info/batch-get/', summary='批量获取书架书籍信息', description='书架卡片书籍详情')
async def guji_shelf_book_info_batch_get(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    from module_guji.service.guji_content_service import GujiContentService

    body = body or {}
    book_ids = body.get('bookIds') or body.get('ids') or []
    rows = await GujiContentService.batch_get_book_services(query_db, book_ids)
    return ResponseUtil.success(data={'rows': rows, 'bookList': rows, 'total': len(rows)})
