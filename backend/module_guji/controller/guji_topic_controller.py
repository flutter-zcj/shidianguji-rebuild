"""
识典古籍模块 - 话题书单控制器

对应原App的 /api/ancientlib/read/topic/*、/topic-book/*、/topic-library/* 接口。
"""

from typing import Annotated, Any

from fastapi import Body, Query, Request, Response

from common.router import APIRouterPro
from module_guji.aspect.guji_auth import CurrentGujiUserDependency, GujiUserModel
from module_guji.aspect.guji_session import GujiDbSession
from module_guji.dao.guji_user_dao import GujiUserDao
from module_guji.service.guji_user_service import GujiTopicService
from utils.response_util import ResponseUtil

topic_controller = APIRouterPro(prefix='/api/ancientlib/read/topic', order_num=240, tags=['识典古籍-话题书单'])


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


@topic_controller.get('/list/', summary='获取话题列表', description='书单广场话题列表')
async def guji_topic_list(
    request: Request,
    query_db: GujiDbSession,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiTopicService.list_topic_services(query_db, None, None, page_num, page_size)
    return ResponseUtil.success(data=result)


@topic_controller.get('/homepage-list/', summary='获取首页话题列表', description='首页话题板块')
async def guji_topic_homepage_list(
    request: Request,
    query_db: GujiDbSession,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 10,
) -> Response:
    result = await GujiTopicService.list_topic_services(query_db, None, None, page_num, page_size)
    return ResponseUtil.success(data=result)


@topic_controller.get('/personal-list/', summary='获取我的话题列表', description='我创建的话题')
async def guji_topic_personal_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiTopicService.list_topic_services(query_db, current_user.user_id, None, page_num, page_size)
    return ResponseUtil.success(data=result)


@topic_controller.get('/followed-list/', summary='获取关注的话题列表', description='我关注的话题')
async def guji_topic_followed_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiTopicService.list_topic_services(query_db, None, None, page_num, page_size)
    return ResponseUtil.success(data=result)


@topic_controller.get('/get/', summary='获取话题详情', description='书单详情页')
async def guji_topic_get(
    request: Request,
    query_db: GujiDbSession,
    topic_id: Annotated[int | None, Query(description='话题ID')] = None,
) -> Response:
    result = await GujiTopicService.get_topic_detail_services(query_db, _int(topic_id))
    return ResponseUtil.success(data=result)


@topic_controller.post('/create/', summary='创建话题书单', description='新建书单')
async def guji_topic_create(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiTopicService.save_topic_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='书单已创建')


@topic_controller.post('/save/', summary='保存话题书单', description='编辑书单基本信息')
async def guji_topic_save(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiTopicService.save_topic_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='书单已保存')


@topic_controller.post('/submit/', summary='提交话题审核', description='书单提交审核')
async def guji_topic_submit(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiTopicService.save_topic_services(
        query_db, current_user.user_id, {**body, 'topicShowStatus': 'reviewing'}
    )
    return ResponseUtil.success(data=result, msg='已提交审核')


@topic_controller.post('/delete/', summary='删除话题书单', description='删除我的书单')
async def guji_topic_delete(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    topic_id = _int(body.get('topicId'))
    await GujiUserDao.delete_topic_book(query_db, topic_id, None)
    return ResponseUtil.success(data={'topicId': topic_id}, msg='书单已删除')


@topic_controller.post('/view/', summary='上报话题浏览', description='书单浏览量上报')
async def guji_topic_view(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


@topic_controller.post('/follow/', summary='关注话题', description='关注书单')
async def guji_topic_follow(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    await GujiUserDao.follow_topic(query_db, current_user.user_id, _int(body.get('topicId')))
    return ResponseUtil.success(msg='已关注')


@topic_controller.post('/unfollow/', summary='取消关注话题', description='取消关注书单')
async def guji_topic_unfollow(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    await GujiUserDao.unfollow_topic(query_db, current_user.user_id, _int(body.get('topicId')))
    return ResponseUtil.success(msg='已取消关注')


@topic_controller.post('/book/add/', summary='书单添加书籍', description='向书单中加入书籍')
async def guji_topic_book_add(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiTopicService.mutate_topic_book_services(query_db, body or {})
    return ResponseUtil.success(data=result, msg='已加入书单')


@topic_controller.post('/book/delete/', summary='书单移除书籍', description='从书单中移除书籍')
async def guji_topic_book_delete(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiTopicService.mutate_topic_book_services(query_db, body or {})
    return ResponseUtil.success(data=result, msg='已移出书单')


@topic_controller.post('/book/delete-all/', summary='清空书单书籍', description='清空书单下所有书籍')
async def guji_topic_book_delete_all(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    await GujiUserDao.delete_topic_book(query_db, _int(body.get('topicId')), None)
    return ResponseUtil.success(msg='书单已清空')


@topic_controller.get('/book/list/', summary='获取书单书籍列表', description='书单详情书籍列表')
async def guji_topic_book_list(
    request: Request,
    query_db: GujiDbSession,
    topic_id: Annotated[int | None, Query(description='话题ID')] = None,
) -> Response:
    rows = await GujiUserDao.get_topic_book_list(query_db, _int(topic_id))
    return ResponseUtil.success(data={'rows': rows, 'bookList': rows, 'total': len(rows)})


@topic_controller.post('/book/list-v2/', summary='获取书单书籍列表V2', description='书单详情书籍列表（V2）')
async def guji_topic_book_list_v2(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    rows = await GujiUserDao.get_topic_book_list(query_db, _int(body.get('topicId')))
    return ResponseUtil.success(data={'rows': rows, 'bookList': rows, 'total': len(rows)})


@topic_controller.post('/book/check/', summary='判断书籍是否在书单', description='书籍详情加入书单状态')
async def guji_topic_book_check(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    rows = await GujiUserDao.get_topic_book_list(query_db, _int(body.get('topicId')))
    book_id = _int(body.get('bookId'))
    exists = any(row.get('bookId') == book_id for row in rows)
    return ResponseUtil.success(data={'inTopic': 1 if exists else 0})


@topic_controller.post('/book/update-order/', summary='调整书单书籍顺序', description='书单内书籍排序')
async def guji_topic_book_update_order(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiTopicService.mutate_topic_book_services(query_db, body or {})
    return ResponseUtil.success(data=result, msg='排序已保存')


@topic_controller.post('/book/update-recommendation/', summary='更新书单推荐语', description='编辑书单内书籍推荐语')
async def guji_topic_book_update_recommendation(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiTopicService.mutate_topic_book_services(query_db, body or {})
    return ResponseUtil.success(data=result, msg='推荐语已保存')


@topic_controller.post('/library/get/', summary='获取话题库详情', description='官方话题库')
async def guji_topic_library_get(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiTopicService.list_topic_services(
        query_db, None, _int(body.get('libraryId')) or None, _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@topic_controller.get('/with-book/list/', summary='获取含书话题列表', description='书籍详情关联书单')
async def guji_topic_with_book_list(
    request: Request,
    query_db: GujiDbSession,
    book_id: Annotated[int | None, Query(description='书籍ID')] = None,
) -> Response:
    result = await GujiTopicService.list_topic_services(query_db, None, None, 1, 20)
    rows = []
    for topic in result.get('rows', []):
        topic_books = topic.get('topicBooks') or []
        if book_id and any(row.get('bookId') == book_id for row in topic_books):
            rows.append(topic)
    return ResponseUtil.success(data={'rows': rows, 'total': len(rows)})
