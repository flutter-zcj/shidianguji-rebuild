"""
识典古籍模块 - 书籍内容控制器

对应原App的 /api/ancientlib/read/book/*、/read/get/*、/read/list/*、/read/category* 等接口。
"""

from typing import Annotated, Any

from fastapi import Body, Query, Request, Response

from common.router import APIRouterPro
from module_guji.aspect.guji_auth import CurrentGujiUserDependency, GujiUserModel
from module_guji.aspect.guji_session import GujiDbSession
from module_guji.dao.guji_content_dao import GujiContentDao
from module_guji.dao.guji_media_dao import GujiMediaDao
from module_guji.service.guji_content_service import GujiContentService
from utils.response_util import ResponseUtil

book_controller = APIRouterPro(prefix='/api/ancientlib/read', order_num=200, tags=['识典古籍-书籍'])


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


@book_controller.get('/book/count', summary='获取古籍总数', description='用于冷启动页展示收录古籍数量')
async def guji_book_count(
    request: Request,
    query_db: GujiDbSession,
) -> Response:
    total = await GujiContentDao.count_book(query_db)
    return ResponseUtil.success(data={'count': total, 'total': total})


@book_controller.post('/book/batch-get/', summary='批量获取书籍信息', description='用于书架、推荐位批量拉取书籍卡片')
async def guji_batch_get_book(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    book_ids = body.get('bookIds') or body.get('ids') or body.get('bookIdList') or []
    if isinstance(book_ids, (str, int)):
        book_ids = [book_ids]
    rows = await GujiContentService.batch_get_book_services(query_db, book_ids)
    return ResponseUtil.success(data={'books': rows, 'rows': rows, 'total': len(rows)})


@book_controller.get('/book/get/', summary='获取书籍详情', description='包含卷信息，needCatalog=1时返回目录')
async def guji_get_book(
    request: Request,
    query_db: GujiDbSession,
    book_id: Annotated[int | None, Query(description='书籍ID')] = None,
    need_catalog: Annotated[int | None, Query(description='是否需要目录')] = None,
) -> Response:
    detail = await GujiContentService.get_book_detail_services(query_db, _int(book_id), _int(need_catalog))
    return ResponseUtil.success(data=detail)


@book_controller.post('/reader-book/get/', summary='获取阅读器书籍信息', description='阅读器进入时拉取书籍与目录')
async def guji_reader_book_get(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    detail = await GujiContentService.get_book_detail_services(
        query_db, _int(body.get('bookId')), _int(body.get('needCatalog') or 1)
    )
    return ResponseUtil.success(data=detail)


@book_controller.post('/reader-book/get/v2', summary='获取阅读器书籍信息V2', description='阅读器进入时拉取书籍与目录（V2）')
async def guji_reader_book_get_v2(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    detail = await GujiContentService.get_book_detail_services(
        query_db, _int(body.get('bookId')), _int(body.get('needCatalog') or 1)
    )
    return ResponseUtil.success(data=detail)


@book_controller.post('/book-with-paragraph/get', summary='获取带段落的书籍信息', description='用于检索结果跳转定位段落')
async def guji_book_with_paragraph_get(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    detail = await GujiContentService.get_book_detail_services(query_db, _int(body.get('bookId')), 1)
    paragraphs, total = await GujiContentDao.get_paragraph_list(
        query_db, _int(body.get('bookId')), _int(body.get('chapterId')) or None, 1, 50
    )
    detail['paragraphs'] = paragraphs
    detail['totalParaNum'] = total
    return ResponseUtil.success(data=detail)


@book_controller.post('/book-version/batch-get', summary='批量获取书籍版本', description='校验本地缓存是否过期')
async def guji_book_version_batch_get(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    book_ids = body.get('bookIds') or body.get('ids') or []
    rows = await GujiContentService.batch_get_book_services(query_db, book_ids)
    versions = [
        {
            'bookId': row.get('bookId'),
            'version': row.get('version'),
            'metaVersion': row.get('metaVersion'),
            'pinYinVersion': row.get('pinYinVersion'),
            'audioVersion': row.get('audioVersion'),
        }
        for row in rows
    ]
    return ResponseUtil.success(data={'rows': versions, 'versions': versions})


@book_controller.get('/book/dynamic-info/get', summary='获取书籍动态信息', description='热度、收藏人数等动态信息')
async def guji_book_dynamic_info(
    request: Request,
    query_db: GujiDbSession,
    book_id: Annotated[int | None, Query(description='书籍ID')] = None,
) -> Response:
    detail = await GujiContentService.get_book_detail_services(query_db, _int(book_id))
    return ResponseUtil.success(
        data={
            'bookId': detail.get('bookId'),
            'popularity': detail.get('popularity'),
            'bookStatus': detail.get('bookStatus'),
            'importanceLevel': detail.get('importanceLevel'),
        }
    )


@book_controller.get('/get/category-tree/', summary='获取传统分类树', description='经史子集四部分类')
async def guji_get_category_tree(
    request: Request,
    query_db: GujiDbSession,
) -> Response:
    tree = await GujiContentService.get_category_tree_services(query_db)
    return ResponseUtil.success(data={'categoryTree': tree, 'rows': tree})


@book_controller.get('/get/nonempty-traditional-category-tree/', summary='获取非空传统分类树', description='仅返回有书的分类')
async def guji_get_nonempty_category_tree(
    request: Request,
    query_db: GujiDbSession,
) -> Response:
    tree = await GujiContentService.get_category_tree_services(query_db)
    tree = [item for item in tree if _int(item.get('bookCount')) > 0]
    return ResponseUtil.success(data={'categoryTree': tree, 'rows': tree})


@book_controller.post('/book-by-category/list', summary='按分类获取书籍', description='分类详情页书籍列表')
async def guji_book_by_category_list(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_book_by_category_services(
        query_db,
        _int(body.get('cateId') or body.get('category') or 0) or None,
        _int(body.get('pageNum') or 1),
        _int(body.get('pageSize') or 20),
    )
    return ResponseUtil.success(data=result)


@book_controller.post('/list/book-by-traditional-category/', summary='按传统分类获取书籍', description='四部分类书籍列表')
async def guji_list_book_by_traditional_category(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_book_by_category_services(
        query_db,
        _int(body.get('cateId') or 0) or None,
        _int(body.get('pageNum') or 1),
        _int(body.get('pageSize') or 20),
    )
    return ResponseUtil.success(data=result)


@book_controller.post('/category-board-detail/get/', summary='获取分类榜单详情', description='分类页板块详情')
async def guji_category_board_detail(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_book_by_category_services(
        query_db, _int(body.get('cateId') or 0) or None, _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data={'boardDetail': result, **result})


@book_controller.post('/count/volume-version/', summary='校验卷版本', description='阅读器校验本地卷版本是否最新')
async def guji_count_volume_version(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    count = await GujiContentDao.count_volume_version(query_db, _int(body.get('volumeId')) or None, body.get('version'))
    return ResponseUtil.success(data={'count': count})


@book_controller.get('/get/volume/', summary='获取卷详情', description='阅读器按卷拉取正文前获取卷信息')
async def guji_get_volume(
    request: Request,
    query_db: GujiDbSession,
    volume_id: Annotated[int | None, Query(description='卷ID')] = None,
) -> Response:
    detail = await GujiContentService.get_volume_detail_services(query_db, _int(volume_id))
    return ResponseUtil.success(data=detail)


@book_controller.post('/book/pages/v2/', summary='获取书籍页内容V2', description='按页拉取正文与译文')
async def guji_book_pages_v2(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_paragraphs_services(
        query_db,
        _int(body.get('bookId')),
        _int(body.get('chapterId')) or None,
        _int(body.get('pageIndex') or body.get('currentPage') or 1),
        _int(body.get('pageSize') or 50),
    )
    return ResponseUtil.success(data=result)


@book_controller.post('/book/pages/v3/', summary='获取书籍页内容V3', description='按页拉取正文与译文（V3）')
async def guji_book_pages_v3(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_paragraphs_services(
        query_db,
        _int(body.get('bookId')),
        _int(body.get('chapterId')) or None,
        _int(body.get('pageIndex') or body.get('currentPage') or 1),
        _int(body.get('pageSize') or 50),
    )
    return ResponseUtil.success(data=result)


@book_controller.post('/book/paragraphs/', summary='获取章节段落V1', description='阅读器正文拉取')
async def guji_book_paragraphs(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_paragraphs_services(
        query_db,
        _int(body.get('bookId')),
        _int(body.get('chapterId')) or None,
        _int(body.get('pageIndex') or body.get('currentPage') or 1),
        _int(body.get('pageSize') or 50),
    )
    return ResponseUtil.success(data=result)


@book_controller.post('/book/paragraphs/v2', summary='获取章节段落V2', description='阅读器正文拉取（V2）')
async def guji_book_paragraphs_v2(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_paragraphs_services(
        query_db,
        _int(body.get('bookId')),
        _int(body.get('chapterId')) or None,
        _int(body.get('pageIndex') or body.get('currentPage') or 1),
        _int(body.get('pageSize') or 50),
    )
    return ResponseUtil.success(data=result)


@book_controller.post('/book/paragraphs/v3/', summary='获取章节段落V3', description='阅读器正文拉取（V3，含注疏与译文）')
async def guji_book_paragraphs_v3(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_paragraphs_services(
        query_db,
        _int(body.get('bookId')),
        _int(body.get('chapterId')) or None,
        _int(body.get('pageIndex') or body.get('currentPage') or 1),
        _int(body.get('pageSize') or 50),
    )
    return ResponseUtil.success(data=result)


@book_controller.post('/history/directory/list/', summary='获取阅读目录增量', description='书架侧最近阅读目录')
async def guji_history_directory_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    from module_guji.service.guji_user_service import GujiHistoryService

    result = await GujiHistoryService.get_history_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@book_controller.get('/book/contributor/list/', summary='获取书籍整理者列表', description='书籍详情整理团队署名')
async def guji_book_contributor_list(
    request: Request,
    query_db: GujiDbSession,
    book_id: Annotated[int | None, Query(description='书籍ID')] = None,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiContentService.get_contributor_services(query_db, _int(book_id), 'contributor', page_num, page_size)
    return ResponseUtil.success(data=result)


@book_controller.get('/book/corrector/list/', summary='获取书籍勘误者列表', description='书籍详情勘误者署名')
async def guji_book_corrector_list(
    request: Request,
    query_db: GujiDbSession,
    book_id: Annotated[int | None, Query(description='书籍ID')] = None,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiContentService.get_contributor_services(query_db, _int(book_id), 'corrector', page_num, page_size)
    return ResponseUtil.success(data=result)


@book_controller.get('/team/get/', summary='获取整理团队信息', description='书籍详情整理团队')
async def guji_team_get(
    request: Request,
    query_db: GujiDbSession,
    team_id: Annotated[int | None, Query(description='团队ID')] = None,
) -> Response:
    from module_guji.service.guji_media_service import GujiHomeService

    result = await GujiHomeService.get_team_services(query_db, _int(team_id))
    return ResponseUtil.success(data=result)


@book_controller.post('/feedback/', summary='提交内容勘误反馈', description='阅读器内原文/译文/拼音错误反馈')
async def guji_feedback(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiContentService.add_feedback_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='感谢反馈')


@book_controller.post('/gen-short-link/', summary='生成分享短链', description='名句/书籍分享')
async def guji_gen_short_link(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    short_link = f"https://www.shidianguji.com/s/{body.get('bizId') or body.get('bookId') or ''}"
    return ResponseUtil.success(data={'shortLink': short_link, 'link': short_link})


@book_controller.post('/copy-frequency/', summary='上报复制频次', description='阅读器复制版权控制')
async def guji_copy_frequency(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'frequency': 1, 'limit': 100})


@book_controller.post('/cold-start/attribution/', summary='冷启动归因上报', description='首次启动渠道归因')
async def guji_cold_start_attribution(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


@book_controller.post('/cold-start/pass-through/', summary='冷启动透传参数', description='阅读器冷启动参数透传')
async def guji_cold_start_pass_through(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data=body or {})


@book_controller.post('/urls/resign', summary='资源URL重签名', description='图片等临时资源换签')
async def guji_urls_resign(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    urls = body.get('urls') or body.get('urlList') or []
    return ResponseUtil.success(data={'urls': urls, 'urlList': urls})


@book_controller.post('/mis-data/get/', summary='获取运营位数据', description='首页/书架运营位兜底数据')
async def guji_mis_data_get(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    rows = await GujiMediaDao.get_recommend_list(query_db, body.get('moduleKey'), body.get('bizType'))
    return ResponseUtil.success(data={'rows': rows, 'total': len(rows)})
