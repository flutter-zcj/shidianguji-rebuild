"""
识典古籍模块 - 书签/笔记/收藏控制器

对应原App的 /api/ancientlib/read/bookmark/*、/review/*、/margin-note/*、/favorites/* 接口。
"""

from typing import Annotated, Any

from fastapi import Body, Query, Request, Response

from common.router import APIRouterPro
from module_guji.aspect.guji_auth import CurrentGujiUserDependency, GujiUserModel
from module_guji.aspect.guji_session import GujiDbSession
from module_guji.dao.guji_content_dao import GujiContentDao
from module_guji.service.guji_content_service import GujiContentService
from module_guji.service.guji_user_service import GujiFavoriteService, GujiNoteService
from utils.response_util import ResponseUtil

note_controller = APIRouterPro(prefix='/api/ancientlib/read', order_num=230, tags=['识典古籍-书签笔记收藏'])


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


# ------------------------------ 书签 ------------------------------


@note_controller.post('/bookmark/add/', summary='新增书签', description='阅读器划线添加书签')
async def guji_bookmark_add(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiNoteService.add_bookmark_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='添加书签成功')


@note_controller.post('/bookmark/batch-add/', summary='批量新增书签', description='阅读器批量同步书签')
async def guji_bookmark_batch_add(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiNoteService.add_bookmark_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='添加书签成功')


@note_controller.get('/bookmark/list/', summary='获取书签列表', description='阅读器/我的书签列表')
async def guji_bookmark_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    book_id: Annotated[int | None, Query(description='书籍ID')] = None,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiNoteService.list_bookmark_services(query_db, current_user.user_id, book_id, page_num, page_size)
    return ResponseUtil.success(data=result)


@note_controller.post('/bookmark/update/', summary='修改书签样式', description='修改划线样式与颜色')
async def guji_bookmark_update(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiNoteService.update_bookmark_services(query_db, body or {})
    return ResponseUtil.success(data=result)


@note_controller.post('/bookmark/del/', summary='删除书签', description='阅读器删除书签')
async def guji_bookmark_del(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiNoteService.delete_bookmark_services(query_db, _int(body.get('bookmarkId') or body.get('bookMarkId')))
    return ResponseUtil.success(data=result, msg='删除成功')


# ------------------------------ 笔记 ------------------------------


@note_controller.post('/review/add/', summary='新增笔记', description='阅读器划线写笔记')
async def guji_review_add(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiNoteService.add_review_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='笔记已保存')


@note_controller.post('/review/batch-add/', summary='批量新增笔记', description='阅读器批量同步笔记')
async def guji_review_batch_add(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiNoteService.add_review_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='笔记已保存')


@note_controller.get('/review/chapter-list/', summary='获取章节笔记列表', description='阅读器查看本章笔记')
async def guji_review_chapter_list(
    request: Request,
    query_db: GujiDbSession,
    book_id: Annotated[int | None, Query(description='书籍ID')] = None,
    chapter_id: Annotated[int | None, Query(description='章节ID')] = None,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiNoteService.list_review_services(query_db, None, book_id, chapter_id, page_num, page_size)
    return ResponseUtil.success(data=result)


@note_controller.get('/review/personal-list/', summary='获取我的笔记列表', description='我的笔记汇总')
async def guji_review_personal_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    book_id: Annotated[int | None, Query(description='书籍ID')] = None,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiNoteService.list_review_services(
        query_db, current_user.user_id, book_id, None, page_num, page_size
    )
    return ResponseUtil.success(data=result)


@note_controller.post('/review/del/', summary='删除笔记', description='阅读器删除笔记')
async def guji_review_del(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiNoteService.delete_review_services(
        query_db, _int(body.get('reviewId') or body.get('commentId') or body.get('review_id'))
    )
    return ResponseUtil.success(data=result, msg='删除成功')


@note_controller.post('/review/feedback/', summary='举报笔记', description='对章节笔记进行举报')
async def guji_review_feedback(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True}, msg='举报已提交')


@note_controller.get('/marked-book/list/', summary='获取有划线的书籍列表', description='我的划线书籍汇总')
async def guji_marked_book_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiNoteService.list_bookmark_services(query_db, current_user.user_id, None, page_num, page_size)
    books: dict[int, dict[str, Any]] = {}
    for row in result.get('rows', []):
        book_id = row.get('bookId')
        if book_id is None:
            continue
        item = books.setdefault(book_id, {'bookId': book_id, 'bookName': '', 'markCount': 0})
        item['markCount'] += 1
    # 补齐真实书名，便于前端按书分组展示
    book_ids = [book_id for book_id in books if book_id]
    if book_ids:
        for book in await GujiContentDao.get_book_list(query_db, book_ids):
            if book.get('bookId') in books:
                books[book['bookId']]['bookName'] = book.get('bookName') or f"书籍 {book['bookId']}"
    for book_id, item in books.items():
        if not item['bookName']:
            item['bookName'] = f'书籍 {book_id}'
    return ResponseUtil.success(data={'rows': list(books.values()), 'total': len(books)})


# ------------------------------ 官方页边注 ------------------------------


@note_controller.post('/margin-note/batch-get/', summary='批量获取页边注', description='阅读器拉取官方页边注')
async def guji_margin_note_batch_get(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    ids = body.get('marginNoteIds') or body.get('ids') or []
    result = await GujiContentService.get_margin_note_services(query_db, [_int(item) for item in ids])
    return ResponseUtil.success(data=result)


@note_controller.get('/margin-note/get/', summary='获取页边注详情', description='阅读器查看单条页边注')
async def guji_margin_note_get(
    request: Request,
    query_db: GujiDbSession,
    margin_note_id: Annotated[int | None, Query(description='页边注ID')] = None,
) -> Response:
    result = await GujiContentService.get_margin_note_services(query_db, [_int(margin_note_id)])
    rows = result.get('marginNoteList') or []
    return ResponseUtil.success(data=rows[0] if rows else {})


# ------------------------------ 通用收藏 ------------------------------


@note_controller.post('/favorites/basic/page/', summary='获取收藏列表', description='我的收藏游标分页')
async def guji_favorites_basic_page(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    offset = _int(body.get('nextPageToken') or 0)
    result = await GujiFavoriteService.list_favorite_services(
        query_db, current_user.user_id, body.get('bizType') or 'quotation', offset, _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@note_controller.post('/favorites/browse/page/', summary='获取浏览收藏列表', description='首页浏览收藏')
async def guji_favorites_browse_page(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    offset = _int(body.get('nextPageToken') or 0)
    result = await GujiFavoriteService.list_favorite_services(
        query_db, current_user.user_id, body.get('bizType') or 'quotation', offset, _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@note_controller.post('/favorites/count/', summary='获取收藏数量', description='我的Tab收藏计数')
async def guji_favorites_count(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    from module_guji.dao.guji_user_dao import GujiUserDao

    body = body or {}
    count = await GujiUserDao.count_favorite(query_db, current_user.user_id, body.get('bizType'))
    return ResponseUtil.success(data={'count': count, 'total': count})


@note_controller.post('/favorites/batch-add/', summary='批量新增收藏', description='名句/书籍批量收藏')
async def guji_favorites_batch_add(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiFavoriteService.add_favorite_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='已收藏')


@note_controller.post('/favorites/batch-del/', summary='批量取消收藏', description='名句/书籍批量取消收藏')
async def guji_favorites_batch_del(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiFavoriteService.delete_favorite_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='已取消收藏')


@note_controller.post('/favorites/batch-check/', summary='批量判断是否已收藏', description='列表页收藏态渲染')
async def guji_favorites_batch_check(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiFavoriteService.check_favorite_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)
