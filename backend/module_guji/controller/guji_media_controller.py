"""
识典古籍模块 - 媒体控制器（听书/播客/视频/讲书课程）

对应原App的 /api/ancientlib/app/explain/*、/app/podcast-book/*、/read/app/{video,audio}* 接口。
"""

from typing import Annotated, Any

from fastapi import Body, Query, Request, Response

from common.router import APIRouterPro
from module_guji.aspect.guji_auth import CurrentGujiUserDependency, GujiUserModel
from module_guji.aspect.guji_session import GujiDbSession
from module_guji.service.guji_media_service import GujiAudioService, GujiCourseService, GujiVideoService
from utils.response_util import ResponseUtil

media_controller = APIRouterPro(prefix='/api/ancientlib', order_num=270, tags=['识典古籍-听书视频讲书'])


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


def _int_list(value: Any) -> list[int]:
    """
    转换为整数列表

    :param value: 待转换值
    :return: 整数列表
    """
    if not value:
        return []
    if isinstance(value, (str, int)):
        value = [value]
    return [item for item in (_int(element) for element in value) if item]


# ------------------------------ 听书 / 播客 ------------------------------


@media_controller.post('/read/book-audio/get', summary='获取书籍音频', description='听书页按书籍拉取音频')
async def guji_book_audio(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiAudioService.get_book_audio_services(query_db, _int(body.get('bookId')) or None)
    return ResponseUtil.success(data=result)


@media_controller.post('/read/linked-book-audio/get', summary='获取关联书籍音频', description='听书页关联音频')
async def guji_linked_book_audio(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiAudioService.get_book_audio_services(query_db, _int(body.get('bookId')) or None)
    return ResponseUtil.success(data=result)


@media_controller.post('/read/audio-lyric/get', summary='获取音频逐句歌词', description='听书页歌词同步')
async def guji_audio_lyric(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiAudioService.get_audio_lyric_services(query_db, _int(body.get('audioId') or body.get('vid')))
    return ResponseUtil.success(data=result)


@media_controller.post('/app/listening-book/list/', summary='获取听书书单', description='听书Tab书单列表')
async def guji_listening_book_list(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiAudioService.get_listening_book_services(
        query_db, _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/app/podcast-book/list/', summary='获取播客列表', description='讲书Tab播客列表')
async def guji_podcast_book_list(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiAudioService.get_podcast_services(
        query_db, _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/app/podcast-book/list/v2/', summary='获取播客列表V2', description='讲书Tab播客列表（V2）')
async def guji_podcast_book_list_v2(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiAudioService.get_podcast_services(
        query_db, _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/read/app/podcast/report-impression/', summary='播客曝光上报', description='播客卡片曝光')
async def guji_podcast_impression(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


# ------------------------------ 视频 ------------------------------


@media_controller.post('/read/app/video-detail/batch-get/', summary='批量获取视频详情', description='视频流卡片详情')
async def guji_video_detail_batch_get(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    video_ids = _int_list(body.get('videoIds') or body.get('ids') or body.get('videoIdList'))
    result = await GujiVideoService.batch_get_video_services(query_db, video_ids)
    return ResponseUtil.success(data=result)


@media_controller.post('/read/app/recommend-video-id/list/', summary='获取推荐视频ID', description='视频流推荐ID列表')
async def guji_recommend_video_id_list(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiVideoService.get_recommend_video_services(
        query_db, 1, _int(body.get('detailNum') or 20), _int_list(body.get('recentPlayVideoIds'))
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/read/app/recommend-video-id/page/', summary='分页获取推荐视频ID', description='视频流分页推荐')
async def guji_recommend_video_id_page(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiVideoService.get_recommend_video_services(
        query_db, _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20), _int_list(body.get('recentPlayVideoIds'))
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/read/app/recommend-video/page/', summary='分页获取推荐视频', description='视频Tab推荐分页')
async def guji_recommend_video_page(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiVideoService.get_recommend_video_services(
        query_db, _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20), None
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/read/app/video-like/', summary='视频点赞', description='视频点赞/取消点赞')
async def guji_video_like(
    request: Request,
    query_db: GujiDbSession,
    current_user: Annotated[GujiUserModel, CurrentGujiUserDependency()],
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


@media_controller.post('/read/app/report-video-impression/', summary='视频曝光上报', description='视频卡片曝光')
async def guji_video_impression(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


@media_controller.get('/read/video-play-auth/get', summary='获取视频播放鉴权', description='视频播放token')
async def guji_video_play_auth(
    request: Request,
    v_id: Annotated[str | None, Query(description='视频ID')] = None,
) -> Response:
    return ResponseUtil.success(data={'videoId': v_id, 'playAuth': f'auth-{v_id}', 'urlEncryptType': 'none'})


@media_controller.post('/read/batch-get-video-course-detail/get/', summary='批量获取视频课程详情', description='视频课详情')
async def guji_batch_video_course_detail(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiVideoService.batch_get_video_course_services(query_db, _int_list(body.get('ids') or body.get('courseIds')))
    return ResponseUtil.success(data=result)


@media_controller.post('/read/recommend-video-by-category/get/', summary='按分类推荐视频', description='分类页视频推荐')
async def guji_recommend_video_by_category(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_recommend_course_services(
        query_db, 'video', _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/read/recommend-video-course-id-by-category/get/', summary='按分类推荐视频课ID', description='分类页视频课推荐')
async def guji_recommend_video_course_id_by_category(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_recommend_course_services(
        query_db, 'video', _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/read/recommend-course-by-category/get/', summary='按分类推荐课程', description='分类页课程推荐')
async def guji_recommend_course_by_category(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_recommend_course_services(
        query_db, 'course', _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/read/recommend-course-id-by-category/get/', summary='按分类推荐课程ID', description='分类页课程ID推荐')
async def guji_recommend_course_id_by_category(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_recommend_course_services(
        query_db, 'course', _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


# ------------------------------ 讲书系列 / 讲解 ------------------------------


@media_controller.get('/app/explain/course-series/list', summary='获取讲书系列列表', description='讲书Tab系列列表')
async def guji_course_series_list(
    request: Request,
    query_db: GujiDbSession,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiCourseService.get_series_list_services(query_db, None, None, page_num, page_size)
    return ResponseUtil.success(data=result)


@media_controller.post('/app/explain/course-series/list', summary='获取讲书系列列表（POST）', description='讲书Tab系列列表')
async def guji_course_series_list_post(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_series_list_services(
        query_db, None, None, _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/app/explain/course-series/batch-get', summary='批量获取讲书系列', description='课程卡片批量取详情')
async def guji_course_series_batch_get(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_series_list_services(query_db, _int_list(body.get('ids') or body.get('seriesIds')), None, 1, 100)
    return ResponseUtil.success(data=result)


@media_controller.get('/app/explain/course-series/search', summary='搜索讲书系列', description='讲书搜索')
async def guji_course_series_search(
    request: Request,
    query_db: GujiDbSession,
    keyword: Annotated[str | None, Query(description='关键词')] = None,
    page_num: Annotated[int, Query(description='页码')] = 1,
    page_size: Annotated[int, Query(description='每页条数')] = 20,
) -> Response:
    result = await GujiCourseService.get_series_list_services(query_db, None, keyword, page_num, page_size)
    return ResponseUtil.success(data=result)


@media_controller.post('/app/explain/course-series/search', summary='搜索讲书系列（POST）', description='讲书搜索')
async def guji_course_series_search_post(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_series_list_services(
        query_db, None, body.get('keyword') or body.get('queryText'), _int(body.get('pageNum') or 1), _int(body.get('pageSize') or 20)
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/app/explain/course-series/get-course-detail', summary='获取课程详情', description='讲书系列详情')
async def guji_course_detail(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_series_detail_services(
        query_db, _int(body.get('seriesId') or body.get('courseId') or body.get('id'))
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/app/explain/course-series/get-course-detail-v2', summary='获取课程详情V2', description='讲书系列详情（V2）')
async def guji_course_detail_v2(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_series_detail_services(
        query_db, _int(body.get('seriesId') or body.get('courseId') or body.get('id'))
    )
    return ResponseUtil.success(data=result)


@media_controller.post('/app/explain/series/get-detail', summary='获取讲书系列详情', description='讲书详情页系列信息')
async def guji_series_detail(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_series_detail_services(query_db, _int(body.get('seriesId') or body.get('id')))
    return ResponseUtil.success(data=result)


@media_controller.post('/app/explain/series/request-update', summary='请求更新讲书系列', description='讲书系列内容更新')
async def guji_series_request_update(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})


@media_controller.post('/app/explain/course-explain/list', summary='获取课程讲解列表', description='课程下讲解音频列表')
async def guji_course_explain_list(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_explain_list_services(query_db, _int(body.get('seriesId')) or None, None)
    return ResponseUtil.success(data=result)


@media_controller.post('/app/explain/list', summary='获取讲解列表', description='首页讲书板块')
async def guji_explain_list(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_explain_list_services(query_db, _int(body.get('seriesId')) or None, None)
    return ResponseUtil.success(data=result)


@media_controller.post('/app/explain/search', summary='搜索讲解', description='讲书内容搜索')
async def guji_explain_search(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    keyword = body.get('keyword') or body.get('queryText') or body.get('query')
    result = await GujiCourseService.get_explain_list_services(query_db, None, keyword)
    return ResponseUtil.success(data=result)


@media_controller.post('/app/explain/paragraph/list', summary='获取段落关联讲解', description='阅读器段落讲解入口')
async def guji_explain_paragraph_list(
    request: Request,
    query_db: GujiDbSession,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    body = body or {}
    result = await GujiCourseService.get_explain_paragraph_services(query_db, _int(body.get('paragraphId')) or None)
    return ResponseUtil.success(data=result)


@media_controller.get('/app/explain/book-link/get', summary='获取讲书关联书籍', description='讲书详情关联典籍')
async def guji_explain_book_link(
    request: Request,
    query_db: GujiDbSession,
    series_id: Annotated[int | None, Query(description='系列ID')] = None,
) -> Response:
    result = await GujiCourseService.get_series_detail_services(query_db, _int(series_id))
    return ResponseUtil.success(data={'bookId': result.get('bookId'), 'bookName': result.get('bookName')})


@media_controller.post('/app/explain/report-impression', summary='讲书曝光上报', description='讲书卡片曝光')
async def guji_explain_impression(
    request: Request,
    body: Annotated[dict[str, Any], Body(default_factory=dict)],
) -> Response:
    return ResponseUtil.success(data={'success': True})
