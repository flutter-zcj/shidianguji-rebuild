"""
识典古籍模块 - 用户域数据库操作层
"""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_guji.dao.guji_content_dao import GujiContentDao
from module_guji.entity.do.guji_user_do import (
    GujiAssistantChat,
    GujiBookmark,
    GujiBookshelf,
    GujiFavorite,
    GujiLevelGiftOrder,
    GujiNotice,
    GujiNoticeRead,
    GujiReadHistory,
    GujiReview,
    GujiTopic,
    GujiTopicBook,
    GujiTopicFollow,
    GujiUserAddress,
    GujiUserClock,
    GujiUserLevel,
    GujiUserPreference,
    GujiUserTag,
)
from utils.common_util import CamelCaseUtil
from utils.page_util import PageUtil


class GujiUserDao:
    """
    古籍用户域数据库操作层
    """

    _rows = GujiContentDao._rows

    # ------------------------------ 书架 ------------------------------

    @classmethod
    async def get_shelf_item(cls, db: AsyncSession, user_id: int, biz_id: str, biz_type: str) -> GujiBookshelf | None:
        """
        获取书架单条记录

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_id: 业务ID
        :param biz_type: 业务类型
        :return: 书架对象
        """
        return (
            await db.execute(
                select(GujiBookshelf).where(
                    GujiBookshelf.user_id == user_id,
                    GujiBookshelf.biz_id == biz_id,
                    GujiBookshelf.shelf_biz_type == biz_type,
                )
            )
        ).scalars().first()

    @classmethod
    async def get_shelf_list(
        cls, db: AsyncSession, user_id: int, biz_type: str, page_num: int, page_size: int, is_page: bool = True
    ) -> Any:
        """
        获取书架列表

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_type: 业务类型
        :param page_num: 页码
        :param page_size: 每页条数
        :param is_page: 是否分页
        :return: 分页对象或列表
        """
        query = (
            select(GujiBookshelf)
            .where(
                GujiBookshelf.user_id == user_id,
                GujiBookshelf.del_flag == '0',
                GujiBookshelf.shelf_biz_type == biz_type if biz_type else True,
            )
            .order_by(GujiBookshelf.last_read_time.desc(), GujiBookshelf.shelf_id.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, is_page)

    @classmethod
    async def upsert_shelf(cls, db: AsyncSession, user_id: int, biz_id: str, biz_type: str, data: dict[str, Any]) -> None:
        """
        新增或更新书架记录

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_id: 业务ID
        :param biz_type: 业务类型
        :param data: 更新字段
        :return:
        """
        shelf = await cls.get_shelf_item(db, user_id, biz_id, biz_type)
        if shelf is None:
            shelf = GujiBookshelf(user_id=user_id, biz_id=biz_id, shelf_biz_type=biz_type)
            db.add(shelf)
        shelf.del_flag = '0'
        for key, value in data.items():
            if value is not None and hasattr(shelf, key):
                setattr(shelf, key, value)
        await db.flush()

    @classmethod
    async def delete_shelf(cls, db: AsyncSession, user_id: int, biz_ids: list[str], biz_type: str) -> None:
        """
        删除书架记录（逻辑删除）

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_ids: 业务ID列表
        :param biz_type: 业务类型
        :return:
        """
        if not biz_ids:
            return
        result = (
            await db.execute(
                select(GujiBookshelf).where(
                    GujiBookshelf.user_id == user_id,
                    GujiBookshelf.biz_id.in_(biz_ids),
                    GujiBookshelf.shelf_biz_type == biz_type,
                )
            )
        ).scalars().all()
        for shelf in result:
            shelf.del_flag = '1'
        await db.flush()

    @classmethod
    async def check_shelf(cls, db: AsyncSession, user_id: int, biz_ids: list[str], biz_type: str) -> dict[str, int]:
        """
        批量判断业务ID是否在书架中

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_ids: 业务ID列表
        :param biz_type: 业务类型
        :return: bizId -> 是否在书架
        """
        result = {biz_id: 0 for biz_id in biz_ids}
        if not biz_ids:
            return result
        rows = (
            await db.execute(
                select(GujiBookshelf.biz_id).where(
                    GujiBookshelf.user_id == user_id,
                    GujiBookshelf.biz_id.in_(biz_ids),
                    GujiBookshelf.shelf_biz_type == biz_type,
                    GujiBookshelf.del_flag == '0',
                )
            )
        ).scalars().all()
        for biz_id in rows:
            result[biz_id] = 1
        return result

    # ------------------------------ 阅读历史 ------------------------------

    @classmethod
    async def upsert_history(cls, db: AsyncSession, user_id: int, biz_id: str, biz_type: str, data: dict[str, Any]) -> None:
        """
        新增或更新阅读历史

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_id: 业务ID
        :param biz_type: 业务类型
        :param data: 更新字段
        :return:
        """
        history = (
            await db.execute(
                select(GujiReadHistory).where(
                    GujiReadHistory.user_id == user_id,
                    GujiReadHistory.biz_id == biz_id,
                    GujiReadHistory.shelf_biz_type == biz_type,
                )
            )
        ).scalars().first()
        if history is None:
            history = GujiReadHistory(user_id=user_id, biz_id=biz_id, shelf_biz_type=biz_type)
            db.add(history)
        history.del_flag = '0'
        for key, value in data.items():
            if value is not None and hasattr(history, key):
                setattr(history, key, value)
        await db.flush()

    @classmethod
    async def get_history_list(
        cls, db: AsyncSession, user_id: int, biz_type: str, page_num: int, page_size: int, is_page: bool = True
    ) -> Any:
        """
        获取阅读历史列表

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_type: 业务类型
        :param page_num: 页码
        :param page_size: 每页条数
        :param is_page: 是否分页
        :return: 分页对象或列表
        """
        query = (
            select(GujiReadHistory)
            .where(
                GujiReadHistory.user_id == user_id,
                GujiReadHistory.del_flag == '0',
                GujiReadHistory.shelf_biz_type == biz_type if biz_type else True,
            )
            .order_by(GujiReadHistory.last_read_time.desc(), GujiReadHistory.history_id.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, is_page)

    @classmethod
    async def get_history_item(cls, db: AsyncSession, user_id: int, biz_id: str, biz_type: str) -> GujiReadHistory | None:
        """
        获取单条阅读历史

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_id: 业务ID
        :param biz_type: 业务类型
        :return: 历史对象
        """
        return (
            await db.execute(
                select(GujiReadHistory).where(
                    GujiReadHistory.user_id == user_id,
                    GujiReadHistory.biz_id == biz_id,
                    GujiReadHistory.shelf_biz_type == biz_type,
                    GujiReadHistory.del_flag == '0',
                )
            )
        ).scalars().first()

    @classmethod
    async def delete_history(cls, db: AsyncSession, user_id: int, biz_ids: list[str], biz_type: str) -> None:
        """
        删除阅读历史（逻辑删除）

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_ids: 业务ID列表
        :param biz_type: 业务类型
        :return:
        """
        if not biz_ids:
            return
        rows = (
            await db.execute(
                select(GujiReadHistory).where(
                    GujiReadHistory.user_id == user_id,
                    GujiReadHistory.biz_id.in_(biz_ids),
                    GujiReadHistory.shelf_biz_type == biz_type,
                )
            )
        ).scalars().all()
        for item in rows:
            item.del_flag = '1'
        await db.flush()

    # ------------------------------ 书签 ------------------------------

    @classmethod
    async def get_bookmark_list(
        cls, db: AsyncSession, user_id: int, book_id: int | None, page_num: int, page_size: int
    ) -> Any:
        """
        获取书签列表

        :param db: orm对象
        :param user_id: 用户ID
        :param book_id: 书籍ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiBookmark)
            .where(
                GujiBookmark.user_id == user_id,
                GujiBookmark.del_flag == '0',
                GujiBookmark.book_id == book_id if book_id else True,
            )
            .order_by(GujiBookmark.bookmark_id.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def add_bookmark(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> GujiBookmark:
        """
        新增书签

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 书签字段
        :return: 书签对象
        """
        bookmark = GujiBookmark(user_id=user_id)
        for key, value in data.items():
            if value is not None and hasattr(bookmark, key):
                setattr(bookmark, key, value)
        db.add(bookmark)
        await db.flush()
        return bookmark

    @classmethod
    async def get_bookmark_by_id(cls, db: AsyncSession, bookmark_id: int) -> GujiBookmark | None:
        """
        根据ID获取书签

        :param db: orm对象
        :param bookmark_id: 书签ID
        :return: 书签对象
        """
        return (await db.execute(select(GujiBookmark).where(GujiBookmark.bookmark_id == bookmark_id))).scalars().first()

    @classmethod
    async def delete_bookmark(cls, db: AsyncSession, bookmark: GujiBookmark) -> None:
        """
        删除书签（逻辑删除）

        :param db: orm对象
        :param bookmark: 书签对象
        :return:
        """
        bookmark.del_flag = '1'
        await db.flush()

    # ------------------------------ 笔记 ------------------------------

    @classmethod
    async def get_review_list(
        cls,
        db: AsyncSession,
        user_id: int | None,
        book_id: int | None,
        chapter_id: int | None,
        page_num: int,
        page_size: int,
    ) -> Any:
        """
        获取笔记列表（章节笔记或我的笔记）

        :param db: orm对象
        :param user_id: 用户ID（我的笔记）
        :param book_id: 书籍ID
        :param chapter_id: 章节ID（章节笔记）
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiReview)
            .where(
                GujiReview.del_flag == '0',
                GujiReview.status == 'normal',
                GujiReview.user_id == user_id if user_id else True,
                GujiReview.book_id == book_id if book_id else True,
                GujiReview.chapter_id == chapter_id if chapter_id else True,
            )
            .order_by(GujiReview.review_id.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def add_review(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> GujiReview:
        """
        新增笔记

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 笔记字段
        :return: 笔记对象
        """
        review = GujiReview(user_id=user_id)
        for key, value in data.items():
            if value is not None and hasattr(review, key):
                setattr(review, key, value)
        db.add(review)
        await db.flush()
        return review

    @classmethod
    async def get_review_by_id(cls, db: AsyncSession, review_id: int) -> GujiReview | None:
        """
        根据ID获取笔记

        :param db: orm对象
        :param review_id: 笔记ID
        :return: 笔记对象
        """
        return (await db.execute(select(GujiReview).where(GujiReview.review_id == review_id))).scalars().first()

    @classmethod
    async def delete_review(cls, db: AsyncSession, review: GujiReview) -> None:
        """
        删除笔记（逻辑删除）

        :param db: orm对象
        :param review: 笔记对象
        :return:
        """
        review.del_flag = '1'
        await db.flush()

    # ------------------------------ 收藏 ------------------------------

    @classmethod
    async def get_favorite_list(
        cls, db: AsyncSession, user_id: int, biz_type: str, offset: int, page_size: int
    ) -> tuple[list[dict[str, Any]], int]:
        """
        获取收藏列表（游标分页）

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_type: 业务类型
        :param offset: 偏移量
        :param page_size: 每页条数
        :return: 收藏列表与总数
        """
        conditions = [
            GujiFavorite.user_id == user_id,
            GujiFavorite.del_flag == '0',
            GujiFavorite.biz_type == biz_type if biz_type else True,
        ]
        total = (
            await db.execute(select(func.count()).select_from(GujiFavorite).where(*conditions))
        ).scalar_one()
        result = (
            await db.execute(
                select(GujiFavorite).where(*conditions).order_by(GujiFavorite.favorite_id.desc()).offset(offset).limit(page_size)
            )
        ).scalars().all()
        return cls._rows(result), total

    @classmethod
    async def count_favorite(cls, db: AsyncSession, user_id: int, biz_type: str | None) -> int:
        """
        统计收藏数量

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_type: 业务类型
        :return: 收藏数量
        """
        return (
            await db.execute(
                select(func.count())
                .select_from(GujiFavorite)
                .where(
                    GujiFavorite.user_id == user_id,
                    GujiFavorite.del_flag == '0',
                    GujiFavorite.biz_type == biz_type if biz_type else True,
                )
            )
        ).scalar_one()

    @classmethod
    async def upsert_favorite(cls, db: AsyncSession, user_id: int, biz_id: str, biz_type: str, data: dict[str, Any]) -> None:
        """
        新增收藏（幂等）

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_id: 业务ID
        :param biz_type: 业务类型
        :param data: 附加字段
        :return:
        """
        favorite = (
            await db.execute(
                select(GujiFavorite).where(
                    GujiFavorite.user_id == user_id, GujiFavorite.biz_id == biz_id, GujiFavorite.biz_type == biz_type
                )
            )
        ).scalars().first()
        if favorite is None:
            favorite = GujiFavorite(user_id=user_id, biz_id=biz_id, biz_type=biz_type)
            db.add(favorite)
        favorite.del_flag = '0'
        for key, value in data.items():
            if value is not None and hasattr(favorite, key):
                setattr(favorite, key, value)
        await db.flush()

    @classmethod
    async def delete_favorite(cls, db: AsyncSession, user_id: int, biz_ids: list[str], biz_type: str) -> None:
        """
        删除收藏（逻辑删除）

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_ids: 业务ID列表
        :param biz_type: 业务类型
        :return:
        """
        if not biz_ids:
            return
        rows = (
            await db.execute(
                select(GujiFavorite).where(
                    GujiFavorite.user_id == user_id,
                    GujiFavorite.biz_id.in_(biz_ids),
                    GujiFavorite.biz_type == biz_type,
                )
            )
        ).scalars().all()
        for item in rows:
            item.del_flag = '1'
        await db.flush()

    @classmethod
    async def check_favorite(cls, db: AsyncSession, user_id: int, biz_ids: list[str], biz_type: str) -> dict[str, int]:
        """
        批量判断是否已收藏

        :param db: orm对象
        :param user_id: 用户ID
        :param biz_ids: 业务ID列表
        :param biz_type: 业务类型
        :return: bizId -> 是否已收藏
        """
        result = {biz_id: 0 for biz_id in biz_ids}
        if not biz_ids:
            return result
        rows = (
            await db.execute(
                select(GujiFavorite.biz_id).where(
                    GujiFavorite.user_id == user_id,
                    GujiFavorite.biz_id.in_(biz_ids),
                    GujiFavorite.biz_type == biz_type,
                    GujiFavorite.del_flag == '0',
                )
            )
        ).scalars().all()
        for biz_id in rows:
            result[biz_id] = 1
        return result

    # ------------------------------ 话题 ------------------------------

    @classmethod
    async def get_topic_by_id(cls, db: AsyncSession, topic_id: int) -> GujiTopic | None:
        """
        根据ID获取话题

        :param db: orm对象
        :param topic_id: 话题ID
        :return: 话题对象
        """
        return (await db.execute(select(GujiTopic).where(GujiTopic.topic_id == topic_id))).scalars().first()

    @classmethod
    async def get_topic_list(
        cls, db: AsyncSession, user_id: int | None, library_id: int | None, page_num: int, page_size: int
    ) -> Any:
        """
        获取话题列表

        :param db: orm对象
        :param user_id: 用户ID（我的话题）
        :param library_id: 话题库ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiTopic)
            .where(
                GujiTopic.del_flag == '0',
                GujiTopic.user_id == user_id if user_id else True,
                GujiTopic.library_id == library_id if library_id else True,
            )
            .order_by(GujiTopic.order_num, GujiTopic.topic_id.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def add_topic(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> GujiTopic:
        """
        新增话题

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 话题字段
        :return: 话题对象
        """
        topic = GujiTopic(user_id=user_id)
        for key, value in data.items():
            if value is not None and hasattr(topic, key):
                setattr(topic, key, value)
        db.add(topic)
        await db.flush()
        return topic

    @classmethod
    async def get_topic_book_list(cls, db: AsyncSession, topic_id: int) -> list[dict[str, Any]]:
        """
        获取话题下书籍列表

        :param db: orm对象
        :param topic_id: 话题ID
        :return: 书籍列表
        """
        result = (
            await db.execute(
                select(GujiTopicBook)
                .where(GujiTopicBook.topic_id == topic_id, GujiTopicBook.del_flag == '0')
                .order_by(GujiTopicBook.order_num, GujiTopicBook.topic_book_id)
            )
        ).scalars().all()
        return cls._rows(result)

    @classmethod
    async def upsert_topic_book(cls, db: AsyncSession, topic_id: int, book_id: int, data: dict[str, Any]) -> None:
        """
        新增或更新话题书籍

        :param db: orm对象
        :param topic_id: 话题ID
        :param book_id: 书籍ID
        :param data: 附加字段
        :return:
        """
        topic_book = (
            await db.execute(
                select(GujiTopicBook).where(GujiTopicBook.topic_id == topic_id, GujiTopicBook.book_id == book_id)
            )
        ).scalars().first()
        if topic_book is None:
            topic_book = GujiTopicBook(topic_id=topic_id, book_id=book_id)
            db.add(topic_book)
        topic_book.del_flag = '0'
        for key, value in data.items():
            if value is not None and hasattr(topic_book, key):
                setattr(topic_book, key, value)
        await db.flush()

    @classmethod
    async def delete_topic_book(cls, db: AsyncSession, topic_id: int, book_id: int | None) -> None:
        """
        删除话题书籍

        :param db: orm对象
        :param topic_id: 话题ID
        :param book_id: 书籍ID，为空时清空话题
        :return:
        """
        query = select(GujiTopicBook).where(GujiTopicBook.topic_id == topic_id)
        if book_id:
            query = query.where(GujiTopicBook.book_id == book_id)
        rows = (await db.execute(query)).scalars().all()
        for item in rows:
            item.del_flag = '1'
        await db.flush()

    @classmethod
    async def follow_topic(cls, db: AsyncSession, user_id: int, topic_id: int) -> None:
        """
        关注话题（幂等）

        :param db: orm对象
        :param user_id: 用户ID
        :param topic_id: 话题ID
        :return:
        """
        follow = (
            await db.execute(
                select(GujiTopicFollow).where(GujiTopicFollow.user_id == user_id, GujiTopicFollow.topic_id == topic_id)
            )
        ).scalars().first()
        if follow is None:
            db.add(GujiTopicFollow(user_id=user_id, topic_id=topic_id))
        else:
            follow.del_flag = '0'
        await db.flush()

    @classmethod
    async def unfollow_topic(cls, db: AsyncSession, user_id: int, topic_id: int) -> None:
        """
        取消关注话题

        :param db: orm对象
        :param user_id: 用户ID
        :param topic_id: 话题ID
        :return:
        """
        follow = (
            await db.execute(
                select(GujiTopicFollow).where(GujiTopicFollow.user_id == user_id, GujiTopicFollow.topic_id == topic_id)
            )
        ).scalars().first()
        if follow is not None:
            follow.del_flag = '1'
            await db.flush()

    # ------------------------------ 偏好 / 打卡 / 等级 ------------------------------

    @classmethod
    async def get_preferences(cls, db: AsyncSession, user_id: int) -> dict[str, Any]:
        """
        获取用户偏好设置

        :param db: orm对象
        :param user_id: 用户ID
        :return: 偏好字典
        """
        rows = (
            await db.execute(
                select(GujiUserPreference).where(GujiUserPreference.user_id == user_id, GujiUserPreference.del_flag == '0')
            )
        ).scalars().all()
        import json

        result: dict[str, Any] = {}
        for row in rows:
            try:
                result[row.preference_key] = json.loads(row.preference_value) if row.preference_value else None
            except (ValueError, TypeError):
                result[row.preference_key] = row.preference_value
        return result

    @classmethod
    async def set_preferences(cls, db: AsyncSession, user_id: int, preferences: dict[str, Any]) -> dict[str, Any]:
        """
        设置用户偏好（增量覆盖）

        :param db: orm对象
        :param user_id: 用户ID
        :param preferences: 偏好键值对
        :return: 完整偏好字典
        """
        import json

        for key, value in preferences.items():
            row = (
                await db.execute(
                    select(GujiUserPreference).where(
                        GujiUserPreference.user_id == user_id, GujiUserPreference.preference_key == key
                    )
                )
            ).scalars().first()
            if row is None:
                row = GujiUserPreference(user_id=user_id, preference_key=key)
                db.add(row)
            row.del_flag = '0'
            row.preference_value = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
        await db.flush()
        return await cls.get_preferences(db, user_id)

    @classmethod
    async def add_clock(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> None:
        """
        新增打卡记录并累加等级信息

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 打卡字段
        :return:
        """
        import datetime

        clock_date = data.get('clock_date') or datetime.datetime.now().strftime('%Y-%m-%d')
        exist = (
            await db.execute(
                select(GujiUserClock).where(
                    GujiUserClock.user_id == user_id, GujiUserClock.clock_date == clock_date, GujiUserClock.del_flag == '0'
                )
            )
        ).scalars().first()
        if exist is None:
            clock = GujiUserClock(user_id=user_id, clock_date=clock_date)
            for key, value in data.items():
                if value is not None and hasattr(clock, key):
                    setattr(clock, key, value)
            db.add(clock)
        else:
            for key, value in data.items():
                if value is not None and hasattr(exist, key):
                    setattr(exist, key, value)
        await db.flush()

    @classmethod
    async def get_clock_list(cls, db: AsyncSession, user_id: int, page_num: int, page_size: int) -> Any:
        """
        获取打卡记录

        :param db: orm对象
        :param user_id: 用户ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiUserClock)
            .where(GujiUserClock.user_id == user_id, GujiUserClock.del_flag == '0')
            .order_by(GujiUserClock.clock_date.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def get_user_level(cls, db: AsyncSession, user_id: int) -> GujiUserLevel | None:
        """
        获取用户等级信息

        :param db: orm对象
        :param user_id: 用户ID
        :return: 等级对象
        """
        return (await db.execute(select(GujiUserLevel).where(GujiUserLevel.user_id == user_id))).scalars().first()

    @classmethod
    async def upsert_user_level(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> GujiUserLevel:
        """
        新增或更新用户等级信息

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 等级字段
        :return: 等级对象
        """
        level = await cls.get_user_level(db, user_id)
        if level is None:
            level = GujiUserLevel(user_id=user_id)
            db.add(level)
        for key, value in data.items():
            if value is not None and hasattr(level, key):
                setattr(level, key, value)
        await db.flush()
        return level

    @classmethod
    async def add_gift_order(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> GujiLevelGiftOrder:
        """
        新增等级权益兑换订单

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 订单字段
        :return: 订单对象
        """
        order = GujiLevelGiftOrder(user_id=user_id)
        for key, value in data.items():
            if value is not None and hasattr(order, key):
                value = json_dump(value) if isinstance(value, (dict, list)) else value  # noqa: PLW2901
                setattr(order, key, value)
        db.add(order)
        await db.flush()
        return order

    @classmethod
    async def get_gift_order_list(cls, db: AsyncSession, user_id: int, page_num: int, page_size: int) -> Any:
        """
        获取权益兑换订单列表

        :param db: orm对象
        :param user_id: 用户ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiLevelGiftOrder)
            .where(GujiLevelGiftOrder.user_id == user_id, GujiLevelGiftOrder.del_flag == '0')
            .order_by(GujiLevelGiftOrder.order_id.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    # ------------------------------ 通知 / 助手 / 地址 / 标签 ------------------------------

    @classmethod
    async def get_notice_list(cls, db: AsyncSession, page_num: int, page_size: int) -> Any:
        """
        获取通知列表

        :param db: orm对象
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiNotice)
            .where(GujiNotice.del_flag == '0', GujiNotice.status == '0')
            .order_by(GujiNotice.notice_id.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def count_unread_notice(cls, db: AsyncSession, user_id: int) -> int:
        """
        统计未读通知数量

        :param db: orm对象
        :param user_id: 用户ID
        :return: 未读数量
        """
        read_ids = select(GujiNoticeRead.notice_id).where(GujiNoticeRead.user_id == user_id)
        return (
            await db.execute(
                select(func.count())
                .select_from(GujiNotice)
                .where(GujiNotice.del_flag == '0', GujiNotice.status == '0', GujiNotice.notice_id.not_in(read_ids))
            )
        ).scalar_one()

    @classmethod
    async def add_assistant_chat(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> GujiAssistantChat:
        """
        新增AI助手会话记录

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 会话字段
        :return: 会话对象
        """
        chat = GujiAssistantChat(user_id=user_id)
        for key, value in data.items():
            if value is not None and hasattr(chat, key):
                setattr(chat, key, value)
        db.add(chat)
        await db.flush()
        return chat

    @classmethod
    async def get_assistant_history(cls, db: AsyncSession, user_id: int, session_id: str | None, limit: int) -> list[dict[str, Any]]:
        """
        获取AI助手会话历史

        :param db: orm对象
        :param user_id: 用户ID
        :param session_id: 会话标识
        :param limit: 条数
        :return: 会话列表
        """
        query = (
            select(GujiAssistantChat)
            .where(
                GujiAssistantChat.user_id == user_id,
                GujiAssistantChat.del_flag == '0',
                GujiAssistantChat.session_id == session_id if session_id else True,
            )
            .order_by(GujiAssistantChat.chat_id.desc())
            .limit(limit)
        )
        return cls._rows((await db.execute(query)).scalars().all())

    @classmethod
    async def get_user_address(cls, db: AsyncSession, user_id: int) -> GujiUserAddress | None:
        """
        获取用户默认收货地址

        :param db: orm对象
        :param user_id: 用户ID
        :return: 地址对象
        """
        return (
            await db.execute(
                select(GujiUserAddress)
                .where(GujiUserAddress.user_id == user_id, GujiUserAddress.del_flag == '0')
                .order_by(GujiUserAddress.is_default.desc(), GujiUserAddress.address_id.desc())
            )
        ).scalars().first()

    @classmethod
    async def save_user_address(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> GujiUserAddress:
        """
        保存用户收货地址

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 地址字段
        :return: 地址对象
        """
        address = await cls.get_user_address(db, user_id)
        if address is None:
            address = GujiUserAddress(user_id=user_id)
            db.add(address)
        for key, value in data.items():
            if value is not None and hasattr(address, key):
                setattr(address, key, value)
        await db.flush()
        return address

    @classmethod
    async def save_user_tags(cls, db: AsyncSession, user_id: int, tag_names: list[str]) -> None:
        """
        保存用户兴趣标签（覆盖式）

        :param db: orm对象
        :param user_id: 用户ID
        :param tag_names: 标签名列表
        :return:
        """
        rows = (
            await db.execute(select(GujiUserTag).where(GujiUserTag.user_id == user_id))
        ).scalars().all()
        for row in rows:
            row.del_flag = '1'
        for name in tag_names:
            db.add(GujiUserTag(user_id=user_id, tag_name=name))
        await db.flush()

    @classmethod
    async def get_user_tags(cls, db: AsyncSession, user_id: int) -> list[dict[str, Any]]:
        """
        获取用户兴趣标签

        :param db: orm对象
        :param user_id: 用户ID
        :return: 标签列表
        """
        result = (
            await db.execute(
                select(GujiUserTag)
                .where(GujiUserTag.user_id == user_id, GujiUserTag.del_flag == '0')
                .order_by(GujiUserTag.tag_id)
            )
        ).scalars().all()
        return cls._rows(result)


def json_dump(value: Any) -> str:
    """
    将字典或列表序列化为JSON字符串

    :param value: 待序列化对象
    :return: JSON字符串
    """
    import json

    return json.dumps(value, ensure_ascii=False)
