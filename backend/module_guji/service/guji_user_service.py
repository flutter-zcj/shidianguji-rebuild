"""
识典古籍模块 - 用户域服务层
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_guji.dao.guji_content_dao import GujiContentDao
from module_guji.dao.guji_user_dao import GujiUserDao


class GujiShelfService:
    """
    书架服务层
    """

    @classmethod
    async def list_shelf_services(
        cls, db: AsyncSession, user_id: int, biz_type: str, page_num: int, page_size: int
    ) -> dict[str, Any]:
        """
        获取书架列表（合并书籍详情）

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_type: 业务类型
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 书架列表
        """
        page_result = await GujiUserDao.get_shelf_list(db, user_id, biz_type, page_num, page_size, True)
        rows = GujiUserDao._rows(page_result.rows)
        book_ids = [int(row['bizId']) for row in rows if str(row.get('bizId', '')).isdigit()]
        book_map = {item['bookId']: item for item in await GujiContentDao.get_book_list(db, book_ids)}
        for row in rows:
            book_id = row.get('bizId')
            row['bookInfo'] = book_map.get(int(book_id)) if str(book_id).isdigit() else None
        return {
            'shelfItemList': rows,
            'rows': rows,
            'total': page_result.total,
            'pageNum': page_num,
            'pageSize': page_size,
        }

    @classmethod
    async def mutate_shelf_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        书架新增/更新（兼容单条与批量）

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 书架数据
        :return: 操作结果
        """
        biz_type = data.get('shelfBizType') or 'book'
        items = data.get('items') or []
        biz_ids: list[str] = []
        if items:
            for index, item in enumerate(items):
                biz_id = str(item.get('bizId') or item.get('bookId') or '')
                if not biz_id:
                    continue
                biz_ids.append(biz_id)
                await GujiUserDao.upsert_shelf(
                    db,
                    user_id,
                    biz_id,
                    biz_type,
                    {
                        'progress': item.get('progress'),
                        'progress_detail': item.get('progressDetail'),
                        'last_read_time': item.get('lastReadTime'),
                        'last_open_time': item.get('lastOpenTime'),
                        'operation_time_ms': item.get('operationTimeMs'),
                        'is_finished': item.get('isFinished'),
                        'group_id': item.get('groupId'),
                    },
                )
        else:
            single_ids = data.get('bizIds') or data.get('bookIds') or []
            if not single_ids and data.get('bookId'):
                single_ids = [data.get('bookId')]
            if not single_ids and data.get('bizId'):
                single_ids = [data.get('bizId')]
            for biz_id in single_ids:
                biz_ids.append(str(biz_id))
                await GujiUserDao.upsert_shelf(
                    db,
                    user_id,
                    str(biz_id),
                    biz_type,
                    {
                        'progress': data.get('progress'),
                        'progress_detail': data.get('progressDetail'),
                        'last_read_time': data.get('lastReadTime'),
                        'last_open_time': data.get('lastOpenTime'),
                        'operation_time_ms': data.get('operationTimeMs'),
                        'is_finished': data.get('isFinished'),
                    },
                )
        return {'successIds': biz_ids, 'total': len(biz_ids)}

    @classmethod
    async def delete_shelf_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        书架删除（兼容单条与批量）

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 删除数据
        :return: 操作结果
        """
        biz_type = data.get('shelfBizType') or 'book'
        biz_ids = [str(item) for item in (data.get('bizIds') or data.get('bookIds') or data.get('groupIds') or [])]
        if not biz_ids and data.get('bookId'):
            biz_ids = [str(data.get('bookId'))]
        if not biz_ids and data.get('bizId'):
            biz_ids = [str(data.get('bizId'))]
        await GujiUserDao.delete_shelf(db, user_id, biz_ids, biz_type)
        return {'successIds': biz_ids, 'total': len(biz_ids)}

    @classmethod
    async def check_shelf_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        批量判断书籍是否在书架

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 查询数据
        :return: 检查结果
        """
        biz_type = data.get('shelfBizType') or 'book'
        biz_ids = [str(item) for item in (data.get('bizIds') or data.get('bookIds') or data.get('groupIds') or [])]
        if not biz_ids and data.get('bookId'):
            biz_ids = [str(data.get('bookId'))]
        result = await GujiUserDao.check_shelf(db, user_id, biz_ids, biz_type)
        return {'shelfStatus': result, 'items': [{'bizId': key, 'inShelf': value} for key, value in result.items()]}


class GujiHistoryService:
    """
    阅读历史服务层
    """

    @classmethod
    async def report_history_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        上报阅读进度（兼容单条与批量）

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 进度数据
        :return: 上报结果
        """
        biz_type = data.get('shelfBizType') or 'book'
        items: list[dict[str, Any]] = []
        for key in (
            'readHistoryList',
            'bookHistoryList',
            'videoHistoryList',
            'seriesHistoryList',
            'podcastHistoryList',
        ):
            if data.get(key):
                items.extend(data[key])
        if not items:
            items = [data]
        count = 0
        for item in items:
            biz_id = str(item.get('bizId') or item.get('bookId') or '')
            if not biz_id:
                continue
            await GujiUserDao.upsert_history(
                db,
                user_id,
                biz_id,
                item.get('shelfBizType') or biz_type,
                {
                    'book_id': int(item['bookId']) if str(item.get('bookId', '')).isdigit() else None,
                    'chapter_id': int(item['chapterId']) if str(item.get('chapterId', '')).isdigit() else None,
                    'chapter_name': item.get('chapterName'),
                    'progress': item.get('progress'),
                    'progress_detail': item.get('progressDetail'),
                    'last_content': item.get('lastContent') or item.get('last_content'),
                    'version': str(item.get('version')) if item.get('version') else None,
                    'last_read_time': item.get('lastReadTime'),
                    'last_open_time': item.get('lastOpenTime'),
                },
            )
            count += 1
        return {'total': count, 'success': True}

    @classmethod
    async def get_history_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        获取阅读历史

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 查询数据
        :return: 历史结果
        """
        biz_type = data.get('shelfBizType') or 'book'
        biz_id = data.get('bizId')
        if biz_id:
            history = await GujiUserDao.get_history_item(db, user_id, str(biz_id), biz_type)
            if history is None:
                return {'historyInfo': None, 'progress': None}
            return {
                'historyInfo': GujiUserDao._rows([history])[0],
                'progress': history.progress,
            }
        page_num = int(data.get('pageNum') or 1)
        page_size = int(data.get('pageSize') or 20)
        page_result = await GujiUserDao.get_history_list(db, user_id, biz_type, page_num, page_size, True)
        rows = GujiUserDao._rows(page_result.rows)
        book_ids = [int(row['bookId']) for row in rows if str(row.get('bookId', '')).isdigit()]
        book_map = {item['bookId']: item for item in await GujiContentDao.get_book_list(db, book_ids)}
        for row in rows:
            row['bookInfo'] = book_map.get(row.get('bookId'))
        return {
            'rows': rows,
            'historyList': rows,
            'total': page_result.total,
            'pageNum': page_num,
            'pageSize': page_size,
        }

    @classmethod
    async def delete_history_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        删除阅读历史

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 删除数据
        :return: 操作结果
        """
        biz_type = data.get('shelfBizType') or 'book'
        biz_ids = [str(item) for item in (data.get('bizIds') or data.get('bookIds') or [])]
        if not biz_ids and data.get('bookId'):
            biz_ids = [str(data.get('bookId'))]
        if not biz_ids and data.get('bizId'):
            biz_ids = [str(data.get('bizId'))]
        await GujiUserDao.delete_history(db, user_id, biz_ids, biz_type)
        return {'successIds': biz_ids, 'total': len(biz_ids)}


class GujiNoteService:
    """
    书签与笔记服务层
    """

    @classmethod
    async def add_bookmark_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        新增书签（兼容批量）

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 书签数据
        :return: 新增结果
        """
        items = data.get('bookMarkList') or []
        if not items:
            items = [data]
        ids = []
        for item in items:
            bookmark = await GujiUserDao.add_bookmark(
                db,
                user_id,
                {
                    'book_id': int(item.get('bookId')) if str(item.get('bookId', '')).isdigit() else None,
                    'chapter_id': int(item.get('chapterId')) if str(item.get('chapterId', '')).isdigit() else None,
                    'chapter_name': item.get('chapterName'),
                    'chapter_start_index': item.get('chapterStartIndex'),
                    'chapter_end_index': item.get('chapterEndIndex'),
                    'marked_text': item.get('markedText'),
                    'marked_text_position': item.get('markedTextPosition'),
                    'bookmark_style': item.get('bookmarkStyle'),
                    'color_style': item.get('colorStyle'),
                    'volume_version': item.get('volumeVersion'),
                    'context': item.get('context'),
                },
            )
            ids.append(bookmark.bookmark_id)
        return {'bookmarkIds': ids, 'total': len(ids)}

    @classmethod
    async def list_bookmark_services(
        cls, db: AsyncSession, user_id: int, book_id: int | None, page_num: int, page_size: int
    ) -> dict[str, Any]:
        """
        获取书签列表

        :param db: orm对象
        :param user_id: 用户ID
        :param book_id: 书籍ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 书签列表
        """
        page_result = await GujiUserDao.get_bookmark_list(db, user_id, book_id, page_num, page_size)
        rows = GujiUserDao._rows(page_result.rows)
        return {'bookMarks': rows, 'rows': rows, 'total': page_result.total}

    @classmethod
    async def delete_bookmark_services(cls, db: AsyncSession, bookmark_id: int) -> dict[str, Any]:
        """
        删除书签

        :param db: orm对象
        :param bookmark_id: 书签ID
        :return: 操作结果
        """
        bookmark = await GujiUserDao.get_bookmark_by_id(db, bookmark_id)
        if bookmark is None:
            return {'success': False, 'message': '书签不存在'}
        await GujiUserDao.delete_bookmark(db, bookmark)
        return {'success': True, 'bookmarkId': bookmark_id}

    @classmethod
    async def update_bookmark_services(cls, db: AsyncSession, data: dict[str, Any]) -> dict[str, Any]:
        """
        修改书签样式

        :param db: orm对象
        :param data: 书签数据
        :return: 操作结果
        """
        bookmark = await GujiUserDao.get_bookmark_by_id(db, int(data.get('bookmarkId') or 0))
        if bookmark is None:
            return {'success': False, 'message': '书签不存在'}
        if data.get('bookmarkStyle'):
            bookmark.bookmark_style = data.get('bookmarkStyle')
        if data.get('colorStyle'):
            bookmark.color_style = data.get('colorStyle')
        await db.flush()
        return {'success': True, 'bookmarkId': bookmark.bookmark_id}

    @classmethod
    async def add_review_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        新增笔记（兼容批量）

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 笔记数据
        :return: 新增结果
        """
        items = data.get('reviewList') or []
        if not items:
            items = [data]
        ids = []
        for item in items:
            review = await GujiUserDao.add_review(
                db,
                user_id,
                {
                    'book_id': int(item.get('bookId')) if str(item.get('bookId', '')).isdigit() else None,
                    'chapter_id': int(item.get('chapterId')) if str(item.get('chapterId', '')).isdigit() else None,
                    'chapter_name': item.get('chapterName'),
                    'chapter_start_index': item.get('chapterStartIndex'),
                    'chapter_end_index': item.get('chapterEndIndex'),
                    'marked_text': item.get('markedText'),
                    'marked_text_position': item.get('markedTextPosition'),
                    'review_type': item.get('reviewType') or 'note',
                    'content': item.get('content'),
                    'volume_version': item.get('volumeVersion'),
                    'volume_status': item.get('volumeStatus'),
                    'context': item.get('context'),
                },
            )
            ids.append(review.review_id)
        return {'reviewIds': ids, 'total': len(ids)}

    @classmethod
    async def list_review_services(
        cls,
        db: AsyncSession,
        user_id: int | None,
        book_id: int | None,
        chapter_id: int | None,
        page_num: int,
        page_size: int,
    ) -> dict[str, Any]:
        """
        获取笔记列表（章节笔记或我的笔记）

        :param db: orm对象
        :param user_id: 用户ID
        :param book_id: 书籍ID
        :param chapter_id: 章节ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 笔记列表
        """
        page_result = await GujiUserDao.get_review_list(db, user_id, book_id, chapter_id, page_num, page_size)
        rows = GujiUserDao._rows(page_result.rows)
        return {'rows': rows, 'reviewList': rows, 'total': page_result.total}

    @classmethod
    async def delete_review_services(cls, db: AsyncSession, review_id: int) -> dict[str, Any]:
        """
        删除笔记

        :param db: orm对象
        :param review_id: 笔记ID
        :return: 操作结果
        """
        review = await GujiUserDao.get_review_by_id(db, review_id)
        if review is None:
            return {'success': False, 'message': '笔记不存在'}
        await GujiUserDao.delete_review(db, review)
        return {'success': True, 'reviewId': review_id}


class GujiFavoriteService:
    """
    通用收藏服务层
    """

    @classmethod
    async def list_favorite_services(
        cls, db: AsyncSession, user_id: int, biz_type: str, offset: int, page_size: int
    ) -> dict[str, Any]:
        """
        获取收藏列表

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_type: 业务类型
        :param offset: 偏移量
        :param page_size: 每页条数
        :return: 收藏列表
        """
        rows, total = await GujiUserDao.get_favorite_list(db, user_id, biz_type, offset, page_size)
        next_offset = offset + len(rows)
        return {
            'rows': rows,
            'total': total,
            'nextPageToken': str(next_offset) if next_offset < total else None,
            'hasMore': next_offset < total,
        }

    @classmethod
    async def add_favorite_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        新增收藏（兼容批量）

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 收藏数据
        :return: 操作结果
        """
        biz_type = data.get('bizType') or 'quotation'
        biz_ids = [str(item) for item in (data.get('bizIds') or [])]
        if not biz_ids and data.get('bizId'):
            biz_ids = [str(data.get('bizId'))]
        for biz_id in biz_ids:
            await GujiUserDao.upsert_favorite(
                db, user_id, biz_id, biz_type, {'title': data.get('title'), 'cover_url': data.get('coverUrl')}
            )
        return {'successIds': biz_ids, 'total': len(biz_ids)}

    @classmethod
    async def delete_favorite_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        删除收藏

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 删除数据
        :return: 操作结果
        """
        biz_type = data.get('bizType') or 'quotation'
        biz_ids = [str(item) for item in (data.get('bizIds') or [])]
        if not biz_ids and data.get('bizId'):
            biz_ids = [str(data.get('bizId'))]
        await GujiUserDao.delete_favorite(db, user_id, biz_ids, biz_type)
        return {'successIds': biz_ids, 'total': len(biz_ids)}

    @classmethod
    async def check_favorite_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        批量判断是否已收藏

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 查询数据
        :return: 检查结果
        """
        biz_type = data.get('bizType') or 'quotation'
        biz_ids = [str(item) for item in (data.get('bizIds') or [])]
        result = await GujiUserDao.check_favorite(db, user_id, biz_ids, biz_type)
        return {'favoriteStatus': result, 'items': [{'bizId': key, 'isFavorite': value} for key, value in result.items()]}


class GujiTopicService:
    """
    话题书单服务层
    """

    @classmethod
    async def list_topic_services(
        cls, db: AsyncSession, user_id: int | None, library_id: int | None, page_num: int, page_size: int
    ) -> dict[str, Any]:
        """
        获取话题列表

        :param db: orm对象
        :param user_id: 用户ID（我的话题）
        :param library_id: 话题库ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 话题列表
        """
        page_result = await GujiUserDao.get_topic_list(db, user_id, library_id, page_num, page_size)
        rows = GujiUserDao._rows(page_result.rows)
        for row in rows:
            row['topicBooks'] = await GujiUserDao.get_topic_book_list(db, row.get('topicId'))
        return {'rows': rows, 'topicList': rows, 'total': page_result.total}

    @classmethod
    async def get_topic_detail_services(cls, db: AsyncSession, topic_id: int) -> dict[str, Any]:
        """
        获取话题详情（含书籍）

        :param db: orm对象
        :param topic_id: 话题ID
        :return: 话题详情
        """
        topic = await GujiUserDao.get_topic_by_id(db, topic_id)
        if topic is None:
            return {}
        detail = GujiUserDao._rows([topic])[0]
        topic_books = await GujiUserDao.get_topic_book_list(db, topic_id)
        book_map = {
            item['bookId']: item
            for item in await GujiContentDao.get_book_list(db, [row.get('bookId') for row in topic_books])
        }
        for row in topic_books:
            row['bookInfo'] = book_map.get(row.get('bookId'))
        detail['topicBooks'] = topic_books
        detail['bookList'] = topic_books
        return detail

    @classmethod
    async def save_topic_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        新增或编辑话题

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 话题数据
        :return: 话题ID
        """
        topic_id = int(data.get('topicId') or 0)
        payload = {
            'title': data.get('title'),
            'description': data.get('description'),
            'cover_url': data.get('coverUrl'),
            'is_private': data.get('isPrivate'),
            'topic_show_status': data.get('topicShowStatus') or 'published',
            'library_id': data.get('libraryId'),
        }
        if topic_id:
            topic = await GujiUserDao.get_topic_by_id(db, topic_id)
            if topic is not None:
                for key, value in payload.items():
                    if value is not None:
                        setattr(topic, key, value)
                await db.flush()
                return {'topicId': topic_id}
        topic = await GujiUserDao.add_topic(db, user_id, payload)
        book_id_list = data.get('bookIdList') or []
        for order, book_id in enumerate(book_id_list):
            await GujiUserDao.upsert_topic_book(db, topic.topic_id, int(book_id), {'order_num': order})
        return {'topicId': topic.topic_id}

    @classmethod
    async def mutate_topic_book_services(cls, db: AsyncSession, data: dict[str, Any]) -> dict[str, Any]:
        """
        话题书籍新增/删除/排序/推荐语

        :param db: orm对象
        :param data: 操作数据
        :return: 操作结果
        """
        topic_id = int(data.get('topicId') or 0)
        if data.get('bookIdOrderMap'):
            for book_id, order in data['bookIdOrderMap'].items():
                await GujiUserDao.upsert_topic_book(db, topic_id, int(book_id), {'order_num': int(order)})
            return {'topicId': topic_id, 'success': True}
        book_id = data.get('bookId')
        if book_id is not None:
            if data.get('recommendation') is not None:
                await GujiUserDao.upsert_topic_book(
                    db, topic_id, int(book_id), {'recommendation': data.get('recommendation')}
                )
            else:
                await GujiUserDao.delete_topic_book(db, topic_id, int(book_id))
            return {'topicId': topic_id, 'success': True}
        for book_id_item in data.get('bookIdList') or []:
            await GujiUserDao.upsert_topic_book(db, topic_id, int(book_id_item), {})
        return {'topicId': topic_id, 'success': True}


class GujiUserService:
    """
    用户设置、打卡、等级、通知、助手服务层
    """

    @classmethod
    async def get_preferences_services(cls, db: AsyncSession, user_id: int) -> dict[str, Any]:
        """
        获取用户阅读偏好

        :param db: orm对象
        :param user_id: 用户ID
        :return: 偏好字典
        """
        return await GujiUserDao.get_preferences(db, user_id)

    @classmethod
    async def set_preferences_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        设置用户阅读偏好

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 偏好数据
        :return: 完整偏好
        """
        preferences = data.get('preferences') or {}
        if not preferences and data.get('preferenceKey'):
            preferences = {data['preferenceKey']: data.get('preferenceValue')}
        if not preferences:
            preferences = {key: value for key, value in data.items() if key not in {'preferences', 'preferenceKey'}}
        return await GujiUserDao.set_preferences(db, user_id, preferences)

    @classmethod
    async def clock_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        阅读打卡

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 打卡数据
        :return: 打卡结果
        """
        await GujiUserDao.add_clock(
            db,
            user_id,
            {
                'book_id': int(data.get('bookId')) if str(data.get('bookId', '')).isdigit() else None,
                'client_timestamp_ms': data.get('clientTimestampMs'),
                'reading_time': data.get('readingTime'),
            },
        )
        level = await GujiUserDao.get_user_level(db, user_id)
        clock_days = (level.clock_days if level else 0) + 1
        continue_days = (level.continue_days if level else 0) + 1
        await GujiUserDao.upsert_user_level(db, user_id, {'clock_days': clock_days, 'continue_days': continue_days})
        return {'clockDays': clock_days, 'continueDays': continue_days, 'success': True}

    @classmethod
    async def get_clock_info_services(cls, db: AsyncSession, user_id: int, page_num: int, page_size: int) -> dict[str, Any]:
        """
        获取打卡信息

        :param db: orm对象
        :param user_id: 用户ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 打卡信息
        """
        page_result = await GujiUserDao.get_clock_list(db, user_id, page_num, page_size)
        rows = GujiUserDao._rows(page_result.rows)
        level = await GujiUserDao.get_user_level(db, user_id)
        return {
            'rows': rows,
            'total': page_result.total,
            'clockDays': level.clock_days if level else 0,
            'continueDays': level.continue_days if level else 0,
            'level': level.level if level else 1,
        }

    @classmethod
    async def get_user_level_services(cls, db: AsyncSession, user_id: int) -> dict[str, Any]:
        """
        获取用户等级与贡献

        :param db: orm对象
        :param user_id: 用户ID
        :return: 等级信息
        """
        level = await GujiUserDao.get_user_level(db, user_id)
        if level is None:
            return {'level': 1, 'clockDays': 0, 'continueDays': 0, 'contributionCount': 0}
        return GujiUserDao._rows([level])[0]

    @classmethod
    async def get_notice_services(cls, db: AsyncSession, user_id: int, page_num: int, page_size: int) -> dict[str, Any]:
        """
        获取通知列表与未读状态

        :param db: orm对象
        :param user_id: 用户ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 通知结果
        """
        page_result = await GujiUserDao.get_notice_list(db, page_num, page_size)
        return {
            'rows': GujiUserDao._rows(page_result.rows),
            'total': page_result.total,
            'unreadCount': await GujiUserDao.count_unread_notice(db, user_id),
        }

    @classmethod
    async def assistant_chat_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        古籍智能助手问答（本地知识库兜底实现）

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 会话数据
        :return: 回答结果
        """
        question = data.get('question') or data.get('content') or ''
        book_id = data.get('bookId')
        answer = ''
        if question:
            page_result = await GujiContentDao.search_paragraph_list(db, question, book_id, 1, 3)
            rows = GujiContentDao._rows(page_result.rows)
            if rows:
                answer = '在《识典古籍》库中找到如下相关原文：\n' + '\n'.join(
                    f"· {row.get('chapterName') or ''}：{row.get('content') or ''}" for row in rows
                )
            else:
                answer = f'暂未在古籍库中检索到与“{question}”相关的原文，可换个关键词或指定具体典籍后重试。'
        chat = await GujiUserDao.add_assistant_chat(
            db,
            user_id,
            {
                'session_id': data.get('sessionId'),
                'book_id': int(book_id) if str(book_id or '').isdigit() else None,
                'chapter_id': int(data.get('chapterId')) if str(data.get('chapterId', '')).isdigit() else None,
                'role': 'assistant',
                'question': question,
                'answer': answer,
            },
        )
        return {
            'sessionId': chat.session_id,
            'chatId': chat.chat_id,
            'question': question,
            'answer': answer,
            'finished': True,
        }

    @classmethod
    async def assistant_history_services(
        cls, db: AsyncSession, user_id: int, session_id: str | None, limit: int
    ) -> dict[str, Any]:
        """
        获取助手会话历史

        :param db: orm对象
        :param user_id: 用户ID
        :param session_id: 会话标识
        :param limit: 条数
        :return: 历史列表
        """
        rows = await GujiUserDao.get_assistant_history(db, user_id, session_id, limit)
        return {'rows': rows, 'total': len(rows)}

    @classmethod
    async def get_contribution_services(cls, db: AsyncSession, user_id: int) -> dict[str, Any]:
        """
        获取用户贡献信息

        :param db: orm对象
        :param user_id: 用户ID
        :return: 贡献信息
        """
        level = await GujiUserDao.get_user_level(db, user_id)
        return {
            'contributionCount': level.contribution_count if level else 0,
            'contributionStr': level.contribution_str if level else '',
            'level': level.level if level else 1,
        }

    @classmethod
    async def save_address_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        保存收货地址

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 地址数据
        :return: 地址信息
        """
        address = await GujiUserDao.save_user_address(
            db,
            user_id,
            {
                'receiver_name': data.get('receiverName'),
                'phone': data.get('phone'),
                'province': data.get('province'),
                'city': data.get('city'),
                'district': data.get('district'),
                'detail': data.get('detail') or data.get('address'),
                'is_default': data.get('isDefault') or 1,
            },
        )
        return GujiUserDao._rows([address])[0]
