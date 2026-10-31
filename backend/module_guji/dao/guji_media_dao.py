"""
识典古籍模块 - 媒体域数据库操作层
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from module_guji.dao.guji_content_dao import GujiContentDao
from module_guji.entity.do.guji_media_do import (
    GujiAudio,
    GujiAudioLyric,
    GujiCourseExplain,
    GujiCourseSeries,
    GujiHomepageBanner,
    GujiPreferencesTag,
    GujiPreferencesTagBook,
    GujiRecommend,
    GujiTeam,
    GujiVideo,
    GujiVideoCourse,
)
from utils.page_util import PageUtil


class GujiMediaDao:
    """
    古籍媒体域数据库操作层
    """

    _rows = GujiContentDao._rows

    # ------------------------------ 音频 ------------------------------

    @classmethod
    async def get_audio_by_id(cls, db: AsyncSession, audio_id: int) -> GujiAudio | None:
        """
        根据ID获取音频

        :param db: orm对象
        :param audio_id: 音频ID
        :return: 音频对象
        """
        return (await db.execute(select(GujiAudio).where(GujiAudio.audio_id == audio_id))).scalars().first()

    @classmethod
    async def get_audio_list_by_book(
        cls, db: AsyncSession, book_id: int | None, listen_type: str | None, page_num: int, page_size: int
    ) -> Any:
        """
        获取书籍音频列表（听书）

        :param db: orm对象
        :param book_id: 书籍ID
        :param listen_type: 收听类型
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiAudio)
            .where(
                GujiAudio.del_flag == '0',
                GujiAudio.status == 'published',
                GujiAudio.book_id == book_id if book_id else True,
                GujiAudio.listen_type == listen_type if listen_type else True,
            )
            .order_by(GujiAudio.podcast_order, GujiAudio.audio_id)
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def get_podcast_list(cls, db: AsyncSession, page_num: int, page_size: int) -> Any:
        """
        获取播客/讲书列表

        :param db: orm对象
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiAudio)
            .where(GujiAudio.del_flag == '0', GujiAudio.status == 'published', GujiAudio.listen_type == 'podcast')
            .order_by(GujiAudio.podcast_order, GujiAudio.audio_id)
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def get_listening_book_list(cls, db: AsyncSession, page_num: int, page_size: int) -> Any:
        """
        获取支持听书的书籍音频列表

        :param db: orm对象
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiAudio)
            .where(GujiAudio.del_flag == '0', GujiAudio.listen_type.in_(['origin', 'translation']))
            .order_by(GujiAudio.audio_id)
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def get_lyric_list(cls, db: AsyncSession, audio_id: int) -> list[dict[str, Any]]:
        """
        获取音频逐句歌词

        :param db: orm对象
        :param audio_id: 音频ID
        :return: 歌词列表
        """
        result = (
            await db.execute(
                select(GujiAudioLyric)
                .where(GujiAudioLyric.audio_id == audio_id, GujiAudioLyric.del_flag == '0')
                .order_by(GujiAudioLyric.audio_index)
            )
        ).scalars().all()
        return cls._rows(result)

    # ------------------------------ 视频 / 课程 ------------------------------

    @classmethod
    async def get_video_list(
        cls, db: AsyncSession, collection_id: int | None, video_ids: list[int] | None, page_num: int, page_size: int
    ) -> Any:
        """
        获取视频列表

        :param db: orm对象
        :param collection_id: 合集ID
        :param video_ids: 视频ID列表
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiVideo)
            .where(
                GujiVideo.del_flag == '0',
                GujiVideo.status == 'published',
                GujiVideo.collection_id == collection_id if collection_id else True,
                GujiVideo.video_id.in_(video_ids) if video_ids else True,
            )
            .order_by(GujiVideo.episode, GujiVideo.video_id)
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def get_video_by_id(cls, db: AsyncSession, video_id: int) -> GujiVideo | None:
        """
        根据ID获取视频

        :param db: orm对象
        :param video_id: 视频ID
        :return: 视频对象
        """
        return (await db.execute(select(GujiVideo).where(GujiVideo.video_id == video_id))).scalars().first()

    @classmethod
    async def get_video_course_list(cls, db: AsyncSession, course_ids: list[int] | None, page_num: int, page_size: int) -> Any:
        """
        获取视频课程列表

        :param db: orm对象
        :param course_ids: 课程ID列表
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiVideoCourse)
            .where(
                GujiVideoCourse.del_flag == '0',
                GujiVideoCourse.status == 'published',
                GujiVideoCourse.course_id.in_(course_ids) if course_ids else True,
            )
            .order_by(GujiVideoCourse.course_id.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def get_video_course_by_id(cls, db: AsyncSession, course_id: int) -> GujiVideoCourse | None:
        """
        根据ID获取视频课程

        :param db: orm对象
        :param course_id: 课程ID
        :return: 课程对象
        """
        return (await db.execute(select(GujiVideoCourse).where(GujiVideoCourse.course_id == course_id))).scalars().first()

    # ------------------------------ 讲书系列 / 讲解 ------------------------------

    @classmethod
    async def get_series_by_id(cls, db: AsyncSession, series_id: int) -> GujiCourseSeries | None:
        """
        根据ID获取讲书系列

        :param db: orm对象
        :param series_id: 系列ID
        :return: 系列对象
        """
        return (await db.execute(select(GujiCourseSeries).where(GujiCourseSeries.series_id == series_id))).scalars().first()

    @classmethod
    async def get_series_list(
        cls, db: AsyncSession, series_ids: list[int] | None, keyword: str | None, page_num: int, page_size: int
    ) -> Any:
        """
        获取讲书系列列表

        :param db: orm对象
        :param series_ids: 系列ID列表
        :param keyword: 关键词
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiCourseSeries)
            .where(
                GujiCourseSeries.del_flag == '0',
                GujiCourseSeries.status == 'published',
                GujiCourseSeries.series_id.in_(series_ids) if series_ids else True,
                GujiCourseSeries.series_title.like(f'%{keyword}%') if keyword else True,
            )
            .order_by(GujiCourseSeries.series_id.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def get_explain_list(cls, db: AsyncSession, series_id: int | None, page_num: int, page_size: int) -> Any:
        """
        获取讲书讲解列表

        :param db: orm对象
        :param series_id: 系列ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiCourseExplain)
            .where(
                GujiCourseExplain.del_flag == '0',
                GujiCourseExplain.status == 'published',
                GujiCourseExplain.series_id == series_id if series_id else True,
            )
            .order_by(GujiCourseExplain.order_num, GujiCourseExplain.explain_id)
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    # ------------------------------ 首页运营位 ------------------------------

    @classmethod
    async def get_banner_list(cls, db: AsyncSession) -> list[dict[str, Any]]:
        """
        获取首页Banner列表

        :param db: orm对象
        :return: Banner列表
        """
        result = (
            await db.execute(
                select(GujiHomepageBanner)
                .where(GujiHomepageBanner.del_flag == '0', GujiHomepageBanner.status == '0')
                .order_by(GujiHomepageBanner.order_num, GujiHomepageBanner.banner_id)
            )
        ).scalars().all()
        return cls._rows(result)

    @classmethod
    async def get_recommend_list(cls, db: AsyncSession, module_key: str | None, biz_type: str | None) -> list[dict[str, Any]]:
        """
        获取首页推荐位

        :param db: orm对象
        :param module_key: 板块键
        :param biz_type: 业务类型
        :return: 推荐列表
        """
        result = (
            await db.execute(
                select(GujiRecommend)
                .where(
                    GujiRecommend.del_flag == '0',
                    GujiRecommend.status == '0',
                    GujiRecommend.module_key == module_key if module_key else True,
                    GujiRecommend.biz_type == biz_type if biz_type else True,
                )
                .order_by(GujiRecommend.order_num, GujiRecommend.recommend_id)
            )
        ).scalars().all()
        return cls._rows(result)

    @classmethod
    async def get_preferences_tag_list(cls, db: AsyncSession) -> list[dict[str, Any]]:
        """
        获取冷启动偏好标签列表

        :param db: orm对象
        :return: 标签列表
        """
        result = (
            await db.execute(
                select(GujiPreferencesTag)
                .where(GujiPreferencesTag.del_flag == '0')
                .order_by(GujiPreferencesTag.order_num)
            )
        ).scalars().all()
        return cls._rows(result)

    @classmethod
    async def get_tag_book_list(cls, db: AsyncSession, tag_id: int) -> list[dict[str, Any]]:
        """
        获取偏好标签关联书籍

        :param db: orm对象
        :param tag_id: 标签ID
        :return: 书籍ID列表
        """
        result = (
            await db.execute(
                select(GujiPreferencesTagBook)
                .where(GujiPreferencesTagBook.tag_id == tag_id, GujiPreferencesTagBook.del_flag == '0')
                .order_by(GujiPreferencesTagBook.order_num)
            )
        ).scalars().all()
        return cls._rows(result)

    @classmethod
    async def get_team_by_id(cls, db: AsyncSession, team_id: int) -> GujiTeam | None:
        """
        根据ID获取整理团队

        :param db: orm对象
        :param team_id: 团队ID
        :return: 团队对象
        """
        return (await db.execute(select(GujiTeam).where(GujiTeam.team_id == team_id))).scalars().first()
