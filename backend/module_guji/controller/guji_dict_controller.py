"""
识典古籍模块 - 字典/实体控制器

对应原App的 /api/ancientlib/dict/*、/read/dictionary/*、/read/entity*、/read/word*、/read/location* 接口。
"""

from typing import Annotated, Any

from fastapi import Body, Query, Request, Response

from common.router import APIRouterPro
from module_guji.aspect.guji_session import GujiDbSession
from module_guji.dao.guji_content_dao import GujiContentDao
from module_guji.service.guji_content_service import GujiContentService
from utils.response_util import ResponseUtil

dict_controller = APIRouterPro(prefix='/api/ancientlib', order_num=260, tags=['识典古籍-字典实体'])


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


# ------------------------------ 查字 ------------------------------


@dict_controller.get('/read/dictionary/get/', summary='查询字词典释义', description='阅读器长按查字')
async def guji_dictionary_get(
    request: Request,
    query_db: GujiDbSession,
    word: Annotated[str | None, Query(description='查询词')] = None,
) -> Response:
    result = await GujiContentService.get_dictionary_services(query_db, word or '')
    return ResponseUtil.success(data=result)


@dict_controller.post('/dict/char-detail', summary='查询单字详情', description='字形、读音、字源详情')
async def guji_char_detail(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_dictionary_services(query_db, body.get('char') or body.get('word') or '')
    return ResponseUtil.success(data=result)


@dict_controller.get('/dict/search-char-by-rad', summary='按部首检字', description='部首检索字形列表')
async def guji_search_char_by_rad(
    request: Request,
    query_db: GujiDbSession,
    rad: Annotated[str | None, Query(description='部首')] = None,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 50,
) -> Response:
    page_result = await GujiContentDao.search_dict_char_by_rad(query_db, rad, page_num, page_size)
    return ResponseUtil.success(data={'rows': GujiContentDao._rows(page_result.rows), 'total': page_result.total})


@dict_controller.post('/dict/search-char-by-rad', summary='按部首检字（POST）', description='部首检索字形列表')
async def guji_search_char_by_rad_post(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    page_result = await GujiContentDao.search_dict_char_by_rad(
        query_db, body.get('rad'), _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 50)
    )
    return ResponseUtil.success(data={'rows': GujiContentDao._rows(page_result.rows), 'total': page_result.total})


@dict_controller.post('/mgt/search-char-by-ids/', summary='批量查询字形', description='OCR校对批量取字形')
async def guji_search_char_by_ids(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    rows = await GujiContentDao.get_dict_char_list(query_db, body.get('ids') or [])
    return ResponseUtil.success(data={'rows': rows, 'total': len(rows)})


# ------------------------------ 实体 ------------------------------


@dict_controller.get('/read/entity/get', summary='获取实体详情', description='人名/地名/官职等实体详情')
async def guji_entity_get(
    request: Request,
    query_db: GujiDbSession,
    entity_id: Annotated[int | None, Query(description='实体ID')] = None,
) -> Response:
    result = await GujiContentService.get_entity_services(query_db, _int(entity_id))
    return ResponseUtil.success(data=result)


@dict_controller.get('/read/entity/search', summary='搜索实体', description='实体检索')
async def guji_entity_search(
    request: Request,
    query_db: GujiDbSession,
    keyword: Annotated[str | None, Query(description='关键词')] = None,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    page_result = await GujiContentDao.search_entity_list(query_db, keyword, page_num, page_size)
    return ResponseUtil.success(data={'rows': GujiContentDao._rows(page_result.rows), 'total': page_result.total})


@dict_controller.post('/read/entity-ref/m-get-by-ids/', summary='批量获取实体引用', description='阅读器段落实体标记')
async def guji_entity_ref_mget(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    refs = body.get('refs') or body.get('ids') or []
    entity_ids = []
    for ref in refs:
        if isinstance(ref, dict):
            entity_ids.append(_int(ref.get('entityId') or ref.get('entity_id')))
        else:
            entity_ids.append(_int(ref))
    rows = await GujiContentDao.get_entity_ref_list(query_db, [item for item in entity_ids if item])
    return ResponseUtil.success(data={'entityRefs': rows, 'rows': rows, 'total': len(rows)})


@dict_controller.get('/read/entity-relation-graph/get', summary='获取实体关系图', description='实体关系图谱')
async def guji_entity_relation_graph(
    request: Request,
    query_db: GujiDbSession,
    book_id: Annotated[int | None, Query(description='书籍ID')] = None,
) -> Response:
    refs = (
        await GujiContentDao.get_entity_ref_list(query_db, []) if not book_id else []
    )
    return ResponseUtil.success(data={'nodes': [], 'edges': [], 'total': 0})


@dict_controller.get('/read/entity-relative-books/get', summary='获取实体关联书籍', description='实体关联典籍')
async def guji_entity_relative_books(
    request: Request,
    query_db: GujiDbSession,
    entity_id: Annotated[int | None, Query(description='实体ID')] = None,
) -> Response:
    rows = await GujiContentDao.get_entity_ref_list(query_db, [_int(entity_id)])
    book_ids = list({row.get('bookId') for row in rows if row.get('bookId')})
    books = await GujiContentDao.get_book_list(query_db, book_ids)
    return ResponseUtil.success(data={'rows': books, 'bookList': books, 'total': len(books)})


@dict_controller.get('/read/entity-relative-paragraphs/get', summary='获取实体关联段落', description='实体在原文中的出处')
async def guji_entity_relative_paragraphs(
    request: Request,
    query_db: GujiDbSession,
    entity_id: Annotated[int | None, Query(description='实体ID')] = None,
) -> Response:
    rows = await GujiContentDao.get_entity_ref_list(query_db, [_int(entity_id)])
    return ResponseUtil.success(data={'rows': rows, 'total': len(rows)})


@dict_controller.get('/read/relative-entity/get', summary='获取相关实体', description='实体相关推荐')
async def guji_relative_entity(
    request: Request,
    query_db: GujiDbSession,
    ref_id: Annotated[int | None, Query(description='引用ID')] = None,
) -> Response:
    return ResponseUtil.success(data={'rows': [], 'total': 0})


# ------------------------------ 字频 / 页面内容 ------------------------------


@dict_controller.post('/read/word-distribution/get/', summary='获取字频分布', description='检索结果字频统计')
async def guji_word_distribution(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    keyword = str(body.get('word') or body.get('queryText') or '')
    page_result = await GujiContentDao.search_paragraph_list(db=query_db, keyword=keyword, book_id=None, page_num=1, page_size=1)
    return ResponseUtil.success(data={'word': keyword, 'total': page_result.total, 'distribution': []})


@dict_controller.post('/read/word-box-page-content/m-get/', summary='批量获取字框页内容', description='OCR校对字框页内容')
async def guji_word_box_page_content(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    page_ids = body.get('pageIds') or body.get('ids') or []
    return ResponseUtil.success(data={'rows': [], 'pageIds': page_ids, 'total': 0})


@dict_controller.post('/read/middle-page/get/', summary='获取中间页内容', description='检索/实体中间页')
async def guji_middle_page(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_dictionary_services(query_db, body.get('word') or '')
    return ResponseUtil.success(data=result)


@dict_controller.get('/read/location/search/', summary='搜索地名', description='历史地名检索')
async def guji_location_search(
    request: Request,
    query_db: GujiDbSession,
    keyword: Annotated[str | None, Query(description='关键词')] = None,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    page_result = await GujiContentDao.search_entity_list(query_db, keyword, page_num, page_size)
    rows = [row for row in GujiContentDao._rows(page_result.rows) if row.get('entityType') == 'location']
    return ResponseUtil.success(data={'rows': rows, 'total': len(rows)})


@dict_controller.post('/read/location-in-dynasty/get/', summary='获取朝代地名', description='按朝代查询地名')
async def guji_location_in_dynasty(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    page_result = await GujiContentDao.search_entity_list(query_db, body.get('dynasty'), 1, 100)
    rows = [
        row
        for row in GujiContentDao._rows(page_result.rows)
        if row.get('entityType') == 'location' and (not body.get('dynasty') or row.get('dynasty') == body.get('dynasty'))
    ]
    return ResponseUtil.success(data={'rows': rows, 'total': len(rows)})


@dict_controller.post('/read/location-map-in-book/get/', summary='获取书内地名地图', description='书籍内地理分布')
async def guji_location_map_in_book(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    page_result = await GujiContentDao.search_entity_list(query_db, None, 1, 200)
    rows = [row for row in GujiContentDao._rows(page_result.rows) if row.get('entityType') == 'location']
    return ResponseUtil.success(data={'rows': rows, 'pointList': rows, 'total': len(rows)})
