"""
识典古籍模块 - 检索控制器

对应原App的 /api/ancientlib/read/search/*、/search-recommend-word/* 等接口。
"""

from typing import Annotated, Any

from fastapi import Body, Query, Request, Response

from common.router import APIRouterPro
from module_guji.aspect.guji_auth import CurrentGujiUserDependency, GujiUserModel
from module_guji.aspect.guji_session import GujiDbSession
from module_guji.dao.guji_media_dao import GujiMediaDao
from module_guji.service.guji_content_service import GujiContentService
from module_guji.service.guji_media_service import GujiVideoService
from utils.response_util import ResponseUtil

search_controller = APIRouterPro(prefix='/api/ancientlib/read', order_num=250, tags=['识典古籍-检索'])


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


def _keyword(body: dict[str, Any]) -> str:
    """
    从请求体中解析检索词（兼容多字段名）

    :param body: 请求体
    :return: 检索词
    """
    return str(body.get('queryText') or body.get('query') or body.get('keyword') or body.get('keywords') or '')


@search_controller.post('/search/book/v1', summary='检索古籍', description='按书名/作者/简介检索书籍')
async def guji_search_book(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.search_book_services(
        query_db, _keyword(body), _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@search_controller.get('/search/book/v1', summary='检索古籍（GET）', description='按书名/作者检索书籍，供H5页面调用')
async def guji_search_book_get(
    request: Request,
    query_db: GujiDbSession,
    query_text: Annotated[str | None, Query(description='检索词')] = None,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiContentService.search_book_services(query_db, query_text or '', page_num, page_size)
    return ResponseUtil.success(data=result)


@search_controller.post('/search/paragraph/v1/', summary='全文检索段落', description='在全书或全库中检索原文')
async def guji_search_paragraph(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.search_paragraph_services(
        query_db,
        _keyword(body),
        _int(body.get('bookId')) or None,
        _int(body.get('pageNum') or 1),
        _int(body.get('pageSize') or 20),
    )
    return ResponseUtil.success(data=result)


@search_controller.get('/search/paragraph/v1/', summary='全文检索段落（GET）', description='在全书或全库中检索原文')
async def guji_search_paragraph_get(
    request: Request,
    query_db: GujiDbSession,
    query_text: Annotated[str | None, Query(description='检索词')] = None,
    book_id: Annotated[int | None, Query(description='书籍ID')] = None,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiContentService.search_paragraph_services(query_db, query_text or '', book_id, page_num, page_size)
    return ResponseUtil.success(data=result)


@search_controller.post('/search/recall/', summary='检索召回上报', description='检索结果点击/曝光召回')
async def guji_search_recall(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


@search_controller.post('/search-recommend-word/get/', summary='获取搜索推荐词', description='搜索框默认推荐词')
async def guji_search_recommend_word(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    rows = await GujiMediaDao.get_recommend_list(query_db, 'search_word', None)
    words = [row.get('title') for row in rows if row.get('title')]
    return ResponseUtil.success(data={'words': words, 'rows': rows, 'total': len(words)})


@search_controller.post('/search-video-by-category/page/', summary='按分类搜索视频', description='视频搜索分页结果')
async def guji_search_video_by_category(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiVideoService.search_video_services(
        query_db, _keyword(body), _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@search_controller.get('/recommend-book/get/', summary='获取推荐书籍', description='书籍详情相关推荐')
async def guji_recommend_book(
    request: Request,
    query_db: GujiDbSession,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 10,
) -> Response:
    result = await GujiContentService.get_book_list_services(query_db, None, None, None, page_num, page_size)
    return ResponseUtil.success(data=result)


@search_controller.post('/get/recommend/', summary='获取综合推荐', description='首页/书籍详情综合推荐')
async def guji_get_recommend(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_book_list_services(
        query_db, None, body.get('traditionalCategory'), body.get('dynastyCategory'), _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 10)
    )
    return ResponseUtil.success(data=result)


@search_controller.get('/get/nonempty-traditional-category-tree/', summary='获取非空传统分类', description='分类页筛选项')
async def guji_nonempty_category_tree(
    request: Request,
    query_db: GujiDbSession,
) -> Response:
    tree = await GujiContentService.get_category_tree_services(query_db)
    tree = [item for item in tree if _int(item.get('bookCount')) > 0]
    return ResponseUtil.success(data={'categoryTree': tree, 'rows': tree})
