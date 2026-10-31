"""
识典古籍模块 - 名句控制器

对应原App的 /api/ancientlib/read/mingju-*、/read/book/quotation*、/read/app/recommend-quotation 接口。
"""

from typing import Annotated, Any

from fastapi import Body, Query, Request, Response

from common.router import APIRouterPro
from module_guji.aspect.guji_auth import CurrentGujiUserDependency, GujiUserModel
from module_guji.aspect.guji_session import GujiDbSession
from module_guji.service.guji_content_service import GujiContentService
from utils.response_util import ResponseUtil

quotation_controller = APIRouterPro(prefix='/api/ancientlib/read', order_num=290, tags=['识典古籍-名句'])


def _int(value: Any, default: int = 0) -> int:
    """
    安全转换为整数

    :param value: 待转换值
    :param default: 默认值
    :return: 整数
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@quotation_controller.post('/book/quotation/page/', summary='获取书籍名句分页', description='书籍详情名句Tab')
async def guji_book_quotation_page(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_quotation_list_services(
        query_db,
        current_user.user_id,
        _int(body.get('bookId')) or None,
        None,
        None,
        _int(body.get('nextPageToken') or 0),
        _int(body.get('pageSize') or 20),
    )
    return ResponseUtil.success(data=result)


@quotation_controller.post('/book/quotation-basic/page/', summary='获取书籍名句简版分页', description='名句·按书浏览')
async def guji_book_quotation_basic_page(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_quotation_list_services(
        query_db,
        current_user.user_id,
        _int(body.get('bookId')) or None,
        None,
        None,
        _int(body.get('nextPageToken') or 0),
        _int(body.get('pageSize') or 20),
    )
    return ResponseUtil.success(data=result)


@quotation_controller.post('/app/recommend-quotation/page/', summary='获取推荐名句', description='名句详情页推荐流')
async def guji_recommend_quotation_page(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_quotation_list_services(
        query_db,
        current_user.user_id,
        None,
        None,
        None,
        _int(body.get('nextPageToken') or 0),
        _int(body.get('pageSize') or 20),
    )
    return ResponseUtil.success(data=result)


@quotation_controller.get('/mingju-category/get', summary='获取名句分类', description='名句分类筛选')
async def guji_mingju_category(
    request: Request,
    query_db: GujiDbSession,
) -> Response:
    result = await GujiContentService.get_quotation_category_services(query_db)
    return ResponseUtil.success(data=result)


@quotation_controller.post('/mingju-category/get', summary='获取名句分类（POST）', description='名句分类筛选')
async def guji_mingju_category_post(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiContentService.get_quotation_category_services(query_db)
    return ResponseUtil.success(data=result)


@quotation_controller.post('/mingju-category-filter/', summary='按条件筛选名句', description='按标签/作者/朝代/体裁筛选')
async def guji_mingju_category_filter(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_quotation_list_services(
        query_db,
        current_user.user_id,
        None,
        _int(body.get('cateId')) or None,
        body.get('tag') or body.get('author') or body.get('dynastyCategory'),
        _int(body.get('nextPageToken') or 0),
        _int(body.get('pageSize') or 20),
    )
    return ResponseUtil.success(data=result)


@quotation_controller.get('/mingju-detail/get', summary='获取名句详情', description='名句详情页')
async def guji_mingju_detail(
    request: Request,
    query_db: GujiDbSession,
    quotation_id: Annotated[int | None, Query(description='名句ID')] = None,
) -> Response:
    result = await GujiContentService.get_quotation_detail_services(query_db, _int(quotation_id))
    return ResponseUtil.success(data=result)


@quotation_controller.post('/mingju-detail/get', summary='获取名句详情（POST）', description='名句详情页')
async def guji_mingju_detail_post(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_quotation_detail_services(query_db, _int(body.get('quotationId') or body.get('mingjuId')))
    return ResponseUtil.success(data=result)
