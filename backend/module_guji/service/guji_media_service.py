"""
识典古籍模块 - 媒体域服务层（听书、播客、视频、讲书课程）
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_guji.dao.guji_content_dao import GujiContentDao
from module_guji.dao.guji_media_dao import GujiMediaDao


class GujiAudioService:
    """
    听书/播客服务层
    """

    @classmethod
    async def get_book_audio_services(cls, db: AsyncSession, book_id: int | None) -> dict[str, Any]:
        """
        获取书籍音频（听书）

        :param db: orm对象
        :param book_id: 书籍ID
        :return: 音频信息
        """
        page_result = await GujiMediaDao.get_audio_list_by_book(db, book_id, None, 1, 200)
        rows = GujiMediaDao._rows(page_result.rows)
        return {
            'bookAudioInfo': {
                'chapterAudios': [row for row in rows if row.get('listenType') == 'origin'],
                'translationAudios': [row for row in rows if row.get('listenType') == 'translation'],
                'contentAudios': rows,
                'contentWithTranslationAudios': rows,
            },
            'audios': rows,
            'total': page_result.total,
        }

    @classmethod
    async def get_podcast_services(cls, db: AsyncSession, page_num: int, page_size: int) -> dict[str, Any]:
        """
        获取播客列表

        :param db: orm对象
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 播客列表
        """
        page_result = await GujiMediaDao.get_podcast_list(db, page_num, page_size)
        return {'rows': GujiMediaDao._rows(page_result.rows), 'total': page_result.total}

    @classmethod
    async def get_listening_book_services(cls, db: AsyncSession, page_num: int, page_size: int) -> dict[str, Any]:
        """
        获取听书书单

        :param db: orm对象
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 听书列表
        """
        page_result = await GujiMediaDao.get_listening_book_list(db, page_num, page_size)
        return {'rows': GujiMediaDao._rows(page_result.rows), 'total': page_result.total}

    @classmethod
    async def get_audio_lyric_services(cls, db: AsyncSession, audio_id: int) -> dict[str, Any]:
        """
        获取音频逐句歌词

        :param db: orm对象
        :param audio_id: 音频ID
        :return: 歌词信息
        """
        rows = await GujiMediaDao.get_lyric_list(db, audio_id)
        return {'lyrics': rows, 'totalLyricPart': len(rows), 'audioId': audio_id}


class GujiVideoService:
    """
    视频与视频课程服务层
    """

    @classmethod
    async def batch_get_video_services(cls, db: AsyncSession, video_ids: list[int]) -> dict[str, Any]:
        """
        批量获取视频详情

        :param db: orm对象
        :param video_ids: 视频ID列表
        :return: 视频列表
        """
        page_result = await GujiMediaDao.get_video_list(db, None, video_ids, 1, max(len(video_ids), 1))
        rows = GujiMediaDao._rows(page_result.rows)
        return {'videoList': rows, 'rows': rows, 'total': len(rows)}

    @classmethod
    async def get_recommend_video_services(
        cls, db: AsyncSession, page_num: int, page_size: int, exclude_ids: list[int] | None
    ) -> dict[str, Any]:
        """
        获取推荐视频分页

        :param db: orm对象
        :param page_num: 页码
        :param page_size: 每页条数
        :param exclude_ids: 需要排除的视频ID
        :return: 推荐视频
        """
        page_result = await GujiMediaDao.get_video_list(db, None, None, page_num, page_size)
        rows = [row for row in GujiMediaDao._rows(page_result.rows) if row.get('videoId') not in (exclude_ids or [])]
        return {'rows': rows, 'videoIdList': [row.get('videoId') for row in rows], 'total': page_result.total}

    @classmethod
    async def search_video_services(cls, db: AsyncSession, keyword: str, page_num: int, page_size: int) -> dict[str, Any]:
        """
        搜索视频

        :param db: orm对象
        :param keyword: 关键词
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 搜索结果
        """
        page_result = await GujiMediaDao.get_video_list(db, None, None, page_num, page_size)
        rows = [
            row
            for row in GujiMediaDao._rows(page_result.rows)
            if not keyword or keyword in (row.get('videoName') or '') or keyword in (row.get('generalAuthor') or '')
        ]
        return {'rows': rows, 'total': len(rows)}

    @classmethod
    async def batch_get_video_course_services(cls, db: AsyncSession, course_ids: list[int]) -> dict[str, Any]:
        """
        批量获取视频课程详情

        :param db: orm对象
        :param course_ids: 课程ID列表
        :return: 课程列表
        """
        page_result = await GujiMediaDao.get_video_course_list(db, course_ids, 1, max(len(course_ids), 1))
        rows = GujiMediaDao._rows(page_result.rows)
        for row in rows:
            video_result = await GujiMediaDao.get_video_list(db, row.get('courseId'), None, 1, 50)
            row['videoList'] = GujiMediaDao._rows(video_result.rows)
        return {'rows': rows, 'courseList': rows, 'total': len(rows)}


class GujiCourseService:
    """
    讲书系列与讲解服务层
    """

    @classmethod
    async def get_series_list_services(
        cls, db: AsyncSession, series_ids: list[int] | None, keyword: str | None, page_num: int, page_size: int
    ) -> dict[str, Any]:
        """
        获取讲书系列列表

        :param db: orm对象
        :param series_ids: 系列ID列表
        :param keyword: 关键词
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 系列列表
        """
        page_result = await GujiMediaDao.get_series_list(db, series_ids, keyword, page_num, page_size)
        return {'rows': GujiMediaDao._rows(page_result.rows), 'seriesList': GujiMediaDao._rows(page_result.rows), 'total': page_result.total}

    @classmethod
    async def get_series_detail_services(cls, db: AsyncSession, series_id: int) -> dict[str, Any]:
        """
        获取讲书系列详情（含讲解列表）

        :param db: orm对象
        :param series_id: 系列ID
        :return: 系列详情
        """
        series = await GujiMediaDao.get_series_by_id(db, series_id)
        if series is None:
            return {}
        detail = GujiMediaDao._rows([series])[0]
        explain_result = await GujiMediaDao.get_explain_list(db, series_id, 1, 200)
        detail['explainList'] = GujiMediaDao._rows(explain_result.rows)
        return detail

    @classmethod
    async def get_explain_list_services(cls, db: AsyncSession, series_id: int | None, keyword: str | None) -> dict[str, Any]:
        """
        获取讲解列表（支持按关键词过滤）

        :param db: orm对象
        :param series_id: 系列ID
        :param keyword: 关键词
        :return: 讲解列表
        """
        page_result = await GujiMediaDao.get_explain_list(db, series_id, 1, 200)
        rows = GujiMediaDao._rows(page_result.rows)
        if keyword:
            rows = [
                row
                for row in rows
                if keyword in (row.get('explainTitle') or '') or keyword in (row.get('content') or '')
            ]
        return {'rows': rows, 'explainList': rows, 'total': len(rows)}

    @classmethod
    async def get_explain_paragraph_services(cls, db: AsyncSession, paragraph_id: int | None) -> dict[str, Any]:
        """
        获取段落关联的讲解

        :param db: orm对象
        :param paragraph_id: 段落ID
        :return: 讲解列表
        """
        if not paragraph_id:
            return {'rows': [], 'total': 0}
        page_result = await GujiMediaDao.get_explain_list(db, None, 1, 500)
        rows = [row for row in GujiMediaDao._rows(page_result.rows) if row.get('paragraphId') == paragraph_id]
        return {'rows': rows, 'explainList': rows, 'total': len(rows)}

    @classmethod
    async def get_recommend_course_services(
        cls, db: AsyncSession, biz_type: str, page_num: int, page_size: int
    ) -> dict[str, Any]:
        """
        按分类推荐课程/视频ID

        :param db: orm对象
        :param biz_type: 推荐类型（course/video）
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 推荐结果
        """
        if biz_type == 'video':
            page_result = await GujiMediaDao.get_video_list(db, None, None, page_num, page_size)
            rows = GujiMediaDao._rows(page_result.rows)
            return {'rows': rows, 'videoIdList': [row.get('videoId') for row in rows], 'total': page_result.total}
        page_result = await GujiMediaDao.get_series_list(db, None, None, page_num, page_size)
        rows = GujiMediaDao._rows(page_result.rows)
        return {'rows': rows, 'seriesIdList': [row.get('seriesId') for row in rows], 'total': page_result.total}


class GujiHomeService:
    """
    首页运营位服务层
    """

    @classmethod
    async def get_preferences_tag_services(cls, db: AsyncSession) -> dict[str, Any]:
        """
        获取冷启动偏好标签

        :param db: orm对象
        :return: 标签列表
        """
        tags = await GujiMediaDao.get_preferences_tag_list(db)
        for tag in tags:
            books = await GujiMediaDao.get_tag_book_list(db, tag.get('tagId'))
            book_ids = [row.get('bookId') for row in books]
            tag['bookList'] = await GujiContentDao.get_book_list(db, book_ids)
        return {'rows': tags, 'tagList': tags, 'total': len(tags)}

    @classmethod
    async def get_team_services(cls, db: AsyncSession, team_id: int) -> dict[str, Any]:
        """
        获取整理团队信息

        :param db: orm对象
        :param team_id: 团队ID
        :return: 团队信息
        """
        team = await GujiMediaDao.get_team_by_id(db, team_id)
        if team is None:
            return {}
        return GujiMediaDao._rows([team])[0]
