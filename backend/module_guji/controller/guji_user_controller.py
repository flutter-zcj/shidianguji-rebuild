"""
识典古籍模块 - 用户与首页控制器

对应原App的 /api/ancientlib/read/app/*、/read/level*、/read/notice/*、/read/assistant/*、/read/channel/* 接口。
"""

from typing import Annotated, Any

from fastapi import Body, Query, Request, Response

from common.router import APIRouterPro
from module_guji.aspect.guji_auth import CurrentGujiUserDependency, GujiUserModel
from module_guji.aspect.guji_session import GujiDbSession
from module_guji.dao.guji_media_dao import GujiMediaDao
from module_guji.service.guji_content_service import GujiContentService
from module_guji.service.guji_media_service import GujiHomeService
from module_guji.service.guji_user_service import GujiUserService
from utils.response_util import ResponseUtil

user_controller = APIRouterPro(prefix='/api/ancientlib/read', order_num=280, tags=['识典古籍-用户与首页'])


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


# ------------------------------ 首页 ------------------------------


@user_controller.post('/app/homepage/', summary='获取首页数据V1', description='首页板块化数据')
async def guji_homepage(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiContentService.get_homepage_services(query_db, current_user.user_id)
    return ResponseUtil.success(data=result)


@user_controller.get('/app/homepage/v2', summary='获取首页数据V2', description='首页板块化数据（V2）')
async def guji_homepage_v2(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
) -> Response:
    result = await GujiContentService.get_homepage_services(query_db, current_user.user_id)
    return ResponseUtil.success(data=result)


@user_controller.post('/app/homepage/v3/', summary='获取首页数据V3', description='首页板块化数据（V3）')
async def guji_homepage_v3(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiContentService.get_homepage_services(query_db, current_user.user_id)
    return ResponseUtil.success(data=result)


@user_controller.post('/app/homepage/v4/', summary='获取首页数据V4', description='首页板块化数据（V4，当前版本）')
async def guji_homepage_v4(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiContentService.get_homepage_services(query_db, current_user.user_id)
    return ResponseUtil.success(data=result)


@user_controller.post('/app/homepage-user/', summary='获取首页用户信息', description='首页问候与打卡状态')
async def guji_homepage_user(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    level = await GujiUserService.get_user_level_services(query_db, current_user.user_id)
    return ResponseUtil.success(data={'userId': current_user.user_id, 'hasLoggedIn': current_user.has_logged_in, **level})


@user_controller.post('/app/feed-book/', summary='获取首页信息流书籍', description='首页推荐信息流')
async def guji_feed_book(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_book_list_services(
        query_db, None, None, None, _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@user_controller.post('/app/feed-book/report-impression/', summary='信息流曝光上报', description='首页信息流曝光')
async def guji_feed_impression(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


@user_controller.get('/homepage-banner/get/', summary='获取首页Banner', description='首页轮播Banner')
async def guji_homepage_banner(
    request: Request,
    query_db: GujiDbSession,
) -> Response:
    rows = await GujiMediaDao.get_banner_list(query_db)
    return ResponseUtil.success(data={'bannerList': rows, 'rows': rows, 'total': len(rows)})


# ------------------------------ 频道 ------------------------------


@user_controller.post('/channel/homepage/', summary='获取频道首页', description='频道页数据')
async def guji_channel_homepage(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiContentService.get_homepage_services(query_db, 0)
    return ResponseUtil.success(data=result)


@user_controller.post('/channel/recommend/', summary='获取频道推荐', description='频道推荐书籍')
async def guji_channel_recommend(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_book_list_services(
        query_db, None, None, None, _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@user_controller.post('/channel/feed/', summary='获取频道信息流', description='频道信息流分页')
async def guji_channel_feed(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiContentService.get_book_list_services(
        query_db, None, None, None, _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@user_controller.get('/channel/classic-reading/', summary='获取经典阅读频道', description='经典阅读栏目')
async def guji_channel_classic_reading(
    request: Request,
    query_db: GujiDbSession,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiContentService.get_book_list_services(query_db, None, None, None, page_num, page_size)
    return ResponseUtil.success(data=result)


@user_controller.post('/channel/book-list-detail/', summary='获取书单详情', description='频道书单详情')
async def guji_channel_book_list_detail(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    from module_guji.service.guji_user_service import GujiTopicService

    body = body or {}
    result = await GujiTopicService.get_topic_detail_services(query_db, _int(body.get('topicId') or body.get('listId')))
    return ResponseUtil.success(data=result)


@user_controller.get('/channel/homepage/recently-entered/', summary='获取最近进入频道', description='频道最近访问')
async def guji_channel_recently_entered(
    request: Request,
    query_db: GujiDbSession,
) -> Response:
    result = await GujiContentService.get_book_list_services(query_db, None, None, None, 1, 10)
    return ResponseUtil.success(data=result)


# ------------------------------ 偏好设置 ------------------------------


@user_controller.post('/app/preferences/get/', summary='获取阅读偏好', description='字号/字体/主题等设置')
async def guji_preferences_get(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiUserService.get_preferences_services(query_db, current_user.user_id)
    return ResponseUtil.success(data={'preferences': result, **result})


@user_controller.post('/app/preferences/set/', summary='设置阅读偏好', description='保存字号/字体/主题等设置')
async def guji_preferences_set(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiUserService.set_preferences_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data={'preferences': result, **result})


@user_controller.get('/app/preferences/options/', summary='获取偏好可选项', description='字号/字体/主题枚举')
async def guji_preferences_options(
    request: Request,
) -> Response:
    return ResponseUtil.success(
        data={
            'fontSize': [14, 16, 18, 20, 22, 24],
            'fontFamily': ['系统默认', '思源宋体', '方正楷体', '方正仿宋'],
            'theme': ['light', 'dark', 'paper', 'protect'],
            'simplifiedMode': ['simplified', 'traditional', 'origin'],
            'translateMode': ['none', 'manual', 'ai'],
            'pageTurn': ['slide', 'scroll', 'simulation'],
        }
    )


@user_controller.post('/app/preferences-tag/list/', summary='获取兴趣标签', description='冷启动兴趣标签')
async def guji_preferences_tag_list(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHomeService.get_preferences_tag_services(query_db)
    return ResponseUtil.success(data=result)


@user_controller.post('/app/preferences-tag-book/list/', summary='获取标签关联书籍', description='冷启动标签书单')
async def guji_preferences_tag_book_list(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiHomeService.get_preferences_tag_services(query_db)
    return ResponseUtil.success(data=result)


# ------------------------------ 打卡 / 等级 ------------------------------


@user_controller.post('/reader-clocks/clock/', summary='阅读打卡', description='每日阅读打卡')
async def guji_reader_clock(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiUserService.clock_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@user_controller.post('/clock-info/get/', summary='获取打卡信息', description='书籍内打卡信息')
async def guji_clock_info(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiUserService.get_clock_info_services(query_db, current_user.user_id, 1, 30)
    return ResponseUtil.success(data=result)


@user_controller.get('/clock-info/page-list/', summary='分页获取打卡记录', description='打卡日历分页')
async def guji_clock_page_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 30,
) -> Response:
    result = await GujiUserService.get_clock_info_services(query_db, current_user.user_id, page_num, page_size)
    return ResponseUtil.success(data=result)


@user_controller.post('/app/my-reading-clock-info/get/', summary='获取我的阅读打卡信息', description='我的Tab打卡概览')
async def guji_my_reading_clock_info(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiUserService.get_clock_info_services(query_db, current_user.user_id, 1, 30)
    return ResponseUtil.success(data=result)


@user_controller.post('/app/reading-time-by-date/get/', summary='获取按日期阅读时长', description='阅读时长折线数据')
async def guji_reading_time_by_date(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiUserService.get_clock_info_services(query_db, current_user.user_id, 1, 100)
    return ResponseUtil.success(data=result)


@user_controller.get('/app/this-week-clock-info/get/', summary='获取本周打卡信息', description='本周打卡概览')
async def guji_this_week_clock_info(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
) -> Response:
    result = await GujiUserService.get_clock_info_services(query_db, current_user.user_id, 1, 7)
    return ResponseUtil.success(data=result)


@user_controller.get('/app/this-week-reading-book/get/', summary='获取本周阅读书籍', description='本周在读书籍')
async def guji_this_week_reading_book(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
) -> Response:
    result = await GujiContentService.get_book_list_services(query_db, None, None, None, 1, 10)
    return ResponseUtil.success(data=result)


@user_controller.get('/level/list/', summary='获取等级规则', description='等级权益说明')
async def guji_level_list(
    request: Request,
) -> Response:
    levels = [
        {'level': index, 'name': name, 'minDays': (index - 1) * 30}
        for index, name in enumerate(['童生', '秀才', '举人', '贡士', '进士', '翰林'], start=1)
    ]
    return ResponseUtil.success(data={'rows': levels, 'total': len(levels)})


@user_controller.get('/user-level/get/', summary='获取用户等级', description='我的等级与贡献')
async def guji_user_level(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
) -> Response:
    result = await GujiUserService.get_user_level_services(query_db, current_user.user_id)
    return ResponseUtil.success(data=result)


@user_controller.get('/level-gift-order/list/', summary='获取权益兑换订单', description='我的兑换订单列表')
async def guji_gift_order_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    from module_guji.dao.guji_user_dao import GujiUserDao

    page_result = await GujiUserDao.get_gift_order_list(query_db, current_user.user_id, page_num, page_size)
    return ResponseUtil.success(data={'rows': GujiUserDao._rows(page_result.rows), 'total': page_result.total})


@user_controller.get('/level-gift-order/confirm/', summary='确认权益兑换订单', description='提交等级权益兑换')
async def guji_gift_order_confirm(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
) -> Response:
    from module_guji.dao.guji_user_dao import GujiUserDao

    order = await GujiUserDao.add_gift_order(query_db, current_user.user_id, {'order_status': 'created'})
    return ResponseUtil.success(data={'orderId': order.order_id}, msg='兑换已提交')


@user_controller.post('/level-gift-order/update-status/', summary='更新权益订单状态', description='物流/完成状态回传')
async def guji_gift_order_update_status(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


# ------------------------------ 通知 / 贡献 / 资料 ------------------------------


@user_controller.get('/notice/list', summary='获取通知列表', description='我的通知消息')
async def guji_notice_list(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiUserService.get_notice_services(query_db, current_user.user_id, page_num, page_size)
    return ResponseUtil.success(data=result)


@user_controller.get('/notice/state', summary='获取通知未读状态', description='我的Tab红点')
async def guji_notice_state(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
) -> Response:
    from module_guji.dao.guji_user_dao import GujiUserDao

    unread = await GujiUserDao.count_unread_notice(query_db, current_user.user_id)
    return ResponseUtil.success(data={'unreadCount': unread, 'hasUnread': unread > 0})


@user_controller.post('/contribution/user/', summary='获取用户贡献', description='我的贡献与勘误统计')
async def guji_contribution_user(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiUserService.get_contribution_services(query_db, current_user.user_id)
    return ResponseUtil.success(data=result)


@user_controller.post('/user-info/sync/', summary='同步用户信息', description='App登录后同步昵称头像')
async def guji_user_info_sync(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    return ResponseUtil.success(
        data={'userId': current_user.user_id, 'nickName': body.get('nickName'), 'avatarUrl': body.get('avatarUrl')}
    )


@user_controller.post('/user-address/get/', summary='获取收货地址', description='权益兑换收货地址')
async def guji_user_address_get(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    from module_guji.dao.guji_user_dao import GujiUserDao

    address = await GujiUserDao.get_user_address(query_db, current_user.user_id)
    if address is None:
        return ResponseUtil.success(data={})
    return ResponseUtil.success(data=GujiUserDao._rows([address])[0])


@user_controller.post('/user-address/save/', summary='保存收货地址', description='权益兑换收货地址')
async def guji_user_address_save(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiUserService.save_address_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result, msg='地址已保存')


@user_controller.get('/user-tag/check/', summary='检查用户兴趣标签', description='是否已完成冷启动选标签')
async def guji_user_tag_check(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
) -> Response:
    from module_guji.dao.guji_user_dao import GujiUserDao

    rows = await GujiUserDao.get_user_tags(query_db, current_user.user_id)
    return ResponseUtil.success(data={'hasTag': len(rows) > 0, 'tags': rows})


@user_controller.post('/user/subscribe/', summary='订阅推送', description='通知订阅开关')
async def guji_user_subscribe(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


# ------------------------------ AI 助手 ------------------------------


@user_controller.post('/assistant/chat/', summary='古籍助手问答', description='基于古籍库内容的智能问答')
async def guji_assistant_chat(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    result = await GujiUserService.assistant_chat_services(query_db, current_user.user_id, body or {})
    return ResponseUtil.success(data=result)


@user_controller.get('/assistant/chat-stream/', summary='古籍助手流式问答', description='流式返回回答（当前实现为一次性返回）')
async def guji_assistant_chat_stream(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    question: Annotated[str | None, Query(description='提问')] = None,
    book_id: Annotated[int | None, Query(description='书籍ID')] = None,
) -> Response:
    result = await GujiUserService.assistant_chat_services(
        query_db, current_user.user_id, {'question': question, 'bookId': book_id}
    )
    return ResponseUtil.success(data=result)


@user_controller.get('/assistant/history/', summary='获取助手会话历史', description='AI助手历史问答')
async def guji_assistant_history(
    request: Request,
    query_db: GujiDbSession,
    current_user: CurrentGujiUserDependency,
    session_id: Annotated[str | None, Query(description='会话标识')] = None,
    limit: Annotated[int, Query(description='条数')] = 50,
) -> Response:
    result = await GujiUserService.assistant_history_services(query_db, current_user.user_id, session_id, limit)
    return ResponseUtil.success(data=result)


@user_controller.post('/assistant/feedback/', summary='助手回答反馈', description='点赞/点踩')
async def guji_assistant_feedback(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


# ------------------------------ 曝光上报 ------------------------------


@user_controller.post('/app/recommend/report-impression/', summary='推荐曝光上报', description='首页推荐曝光')
async def guji_recommend_impression(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


@user_controller.post('/app/topic/report-impression/', summary='话题曝光上报', description='话题卡片曝光')
async def guji_topic_impression(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


@user_controller.post('/app/quotation/report-impression/', summary='名句曝光上报', description='名句卡片曝光')
async def guji_quotation_impression(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


@user_controller.post('/ad/report/', summary='广告曝光上报', description='广告位曝光')
async def guji_ad_report(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})
