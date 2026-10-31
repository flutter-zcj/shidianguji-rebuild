"""
识典古籍模块 - 阅读历史控制器

对应原App的 /api/ancientlib/read/history/* 系列接口。
"""

from typing import Annotated, Any

from fastapi import Body, Query, Request, Response

from common.router import APIRouterPro
from module_guji.aspect.guji_auth import CurrentGujiUserDependency, GujiUserModel
from module_guji.aspect.guji_session import GujiDbSession
from module_guji.service.guji_user_service import GujiHistoryService, GujiUserService
from utils.response_util import ResponseUtil

history_controller = APIRouterPro(prefix='/api/ancientlib/read/history', order_num=220, tags=['识典古籍-阅读历史'])


@history_controller.post('/report/', summary='上报阅读进度', description='阅读器翻页/退出时上报进度')
async def guji_history_report(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.report_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.post('/batch-report/', summary='批量上报阅读进度', description='书架侧批量上报进度')
async def guji_history_batch_report(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.report_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.post('/batch-report/v3/', summary='批量上报阅读进度V3', description='多业务统一上报（V3）')
async def guji_history_batch_report_v3(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.report_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.get('/get/', summary='获取阅读进度', description='进入阅读器时恢复进度')
async def guji_history_get(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    book_id: Annotated[str | None, Query(description='书籍ID')] = None,
    biz_id: Annotated[str | None, Query(description='业务ID')] = None,
    shelf_biz_type: Annotated[str | None, Query(description='业务类型')] = None,
) -> Response:
    result = await GujiHistoryService.get_history_services(
        query_db, current_user.user_id, {'bookId': book_id, 'bizId': biz_id, 'shelfBizType': shelf_biz_type}
    )
    return ResponseUtil.success(data=result)


@history_controller.post('/get/v3/', summary='获取阅读进度V3', description='进入阅读器时恢复进度（V3）')
async def guji_history_get_v3(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.get_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.post('/get/v4/', summary='获取阅读进度V4', description='进入阅读器时恢复进度（V4）')
async def guji_history_get_v4(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.get_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.get('/list/', summary='获取阅读历史列表', description='书架最近阅读列表')
async def guji_history_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
    shelf_biz_type: Annotated[str | None, Query(description='业务类型')] = None,
) -> Response:
    result = await GujiHistoryService.get_history_services(
        query_db, current_user.user_id, {'pageNum': page_num, 'pageSize': page_size, 'shelfBizType': shelf_biz_type}
    )
    return ResponseUtil.success(data=result)


@history_controller.post('/list/v2', summary='获取阅读历史列表V2', description='书架最近阅读列表（V2）')
async def guji_history_list_v2(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.get_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.post('/list/v3/', summary='获取阅读历史列表V3', description='书架最近阅读列表（V3）')
async def guji_history_list_v3(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.get_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.post('/batch-get/v4/', summary='批量获取阅读历史V4', description='批量拉取多业务历史（V4）')
async def guji_history_batch_get_v4(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.get_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.post('/delete/', summary='删除阅读历史', description='书架删除单条历史')
async def guji_history_delete(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.delete_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.post('/batch-delete/v3/', summary='批量删除阅读历史V3', description='书架批量删除历史（V3）')
async def guji_history_batch_delete_v3(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.delete_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.post('/batch-delete/v4/', summary='批量删除阅读历史V4', description='书架批量删除历史（V4）')
async def guji_history_batch_delete_v4(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.delete_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.post('/directory/list/', summary='获取最近阅读目录', description='书架侧最近阅读章节目录')
async def guji_history_directory_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHistoryService.get_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@history_controller.post('/reading-time/report/', summary='上报阅读时长', description='阅读器累计阅读时长上报')
async def guji_reading_time_report(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiUserService.clock_services(
        query_db,
        current_user.user_id,
        {'bookId': body.get('bookId'), 'readingTime': body.get('readingTime'), 'clientTimestampMs': body.get('clientTimestampMs')},
    )
    return ResponseUtil.success(data=result)
