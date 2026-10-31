from collections.abc import Sequence
from typing import Any

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_guji.entity.do.guji_do import (
    GujiAudio,
    GujiBook,
    GujiBookshelf,
    GujiChapter,
    GujiParagraph,
    GujiReadHistory,
)
from module_guji.entity.vo.guji_vo import (
    GujiBookPageQueryModel,
    GujiParagraphPageQueryModel,
)
from utils.page_util import PageUtil
from utils.time_util import TimezoneUtil


class GujiDao:
    """
    古籍阅读平台数据库操作层
    """

    @classmethod
    async def get_book_list(
        cls, db: AsyncSession, query_object: GujiBookPageQueryModel, is_page: bool = True
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取古籍书目分页列表

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否分页
        :return: 书目列表
        """
        conditions = [GujiBook.del_flag == '0', GujiBook.status == '0']
        if query_object.book_name:
            conditions.append(GujiBook.book_name.like(f'%{query_object.book_name}%'))
        if query_object.category:
            conditions.append(GujiBook.category == query_object.category)
        if query_object.dynasty:
            conditions.append(GujiBook.dynasty == query_object.dynasty)
        query = select(GujiBook).where(*conditions).order_by(GujiBook.book_id.asc())
        result = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)
        return result

    @classmethod
    async def get_book_detail(cls, db: AsyncSession, book_id: int) -> GujiBook | None:
        """
        获取古籍书目详情

        :param db: orm对象
        :param book_id: 书目ID
        :return: 书目详情对象
        """
        return (
            (
                await db.execute(
                    select(GujiBook).where(GujiBook.book_id == book_id, GujiBook.del_flag == '0')
                )
            )
            .scalars()
            .first()
        )

    @classmethod
    async def get_chapter_list(cls, db: AsyncSession, book_id: int) -> Sequence[GujiChapter]:
        """
        获取书目章节目录

        :param db: orm对象
        :param book_id: 书目ID
        :return: 章节列表
        """
        return (
            (
                await db.execute(
                    select(GujiChapter).where(GujiChapter.book_id == book_id).order_by(GujiChapter.chapter_no.asc())
                )
            )
            .scalars()
            .all()
        )

    @classmethod
    async def get_paragraph_page(
        cls, db: AsyncSession, query_object: GujiParagraphPageQueryModel, is_page: bool = True
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取章节段落分页

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否分页
        :return: 段落分页列表
        """
        query = (
            select(GujiParagraph)
            .where(GujiParagraph.chapter_id == query_object.chapter_id)
            .order_by(GujiParagraph.para_seq.asc())
        )
        result = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)
        return result

    @classmethod
    async def get_bookshelf_list(cls, db: AsyncSession, user_id: int) -> list[dict[str, Any]]:
        """
        获取用户书架列表（含书目信息与最近阅读进度）

        :param db: orm对象
        :param user_id: 用户ID
        :return: 书架条目字典列表
        """
        rows = (
            await db.execute(
                select(
                    GujiBookshelf.shelf_id,
                    GujiBookshelf.book_id,
                    GujiBook.book_name,
                    GujiBook.author,
                    GujiBook.dynasty,
                    GujiBook.category,
                    GujiBook.cover,
                    GujiBook.chapter_count,
                    GujiBookshelf.last_chapter_id,
                    GujiChapter.chapter_name.label('last_chapter_name'),
                    GujiBookshelf.last_paragraph_id,
                    GujiBookshelf.update_time,
                )
                .join(GujiBook, GujiBook.book_id == GujiBookshelf.book_id)
                .outerjoin(GujiChapter, GujiChapter.chapter_id == GujiBookshelf.last_chapter_id)
                .where(GujiBookshelf.user_id == user_id)
                .order_by(GujiBookshelf.update_time.desc())
            )
        ).all()
        return [dict(row._mapping) for row in rows]

    @classmethod
    async def get_bookshelf_item(cls, db: AsyncSession, user_id: int, book_id: int) -> GujiBookshelf | None:
        """
        查询用户书架中指定书目

        :param db: orm对象
        :param user_id: 用户ID
        :param book_id: 书目ID
        :return: 书架条目对象
        """
        return (
            (
                await db.execute(
                    select(GujiBookshelf).where(
                        GujiBookshelf.user_id == user_id, GujiBookshelf.book_id == book_id
                    )
                )
            )
            .scalars()
            .first()
        )

    @classmethod
    async def add_bookshelf(cls, db: AsyncSession, user_id: int, book_id: int) -> None:
        """
        加入书架（已存在则仅刷新时间）

        :param db: orm对象
        :param user_id: 用户ID
        :param book_id: 书目ID
        :return: None
        """
        item = await cls.get_bookshelf_item(db, user_id, book_id)
        if item:
            item.update_time = TimezoneUtil.utc_now()
            await db.flush()
            return
        new_item = GujiBookshelf(user_id=user_id, book_id=book_id)
        new_item.create_time = TimezoneUtil.utc_now()
        new_item.update_time = new_item.create_time
        db.add(new_item)
        await db.flush()

    @classmethod
    async def delete_bookshelf(cls, db: AsyncSession, user_id: int, book_id: int) -> None:
        """
        移出书架

        :param db: orm对象
        :param user_id: 用户ID
        :param book_id: 书目ID
        :return: None
        """
        await db.execute(
            delete(GujiBookshelf).where(
                GujiBookshelf.user_id == user_id, GujiBookshelf.book_id == book_id
            )
        )

    @classmethod
    async def update_bookshelf_progress(
        cls, db: AsyncSession, user_id: int, book_id: int, chapter_id: int, paragraph_id: int
    ) -> None:
        """
        更新书架最近阅读进度

        :param db: orm对象
        :param user_id: 用户ID
        :param book_id: 书目ID
        :param chapter_id: 章节ID
        :param paragraph_id: 段落ID
        :return: None
        """
        item = await cls.get_bookshelf_item(db, user_id, book_id)
        now = TimezoneUtil.utc_now()
        if item:
            item.last_chapter_id = chapter_id
            item.last_paragraph_id = paragraph_id
            item.update_time = now
        else:
            new_item = GujiBookshelf(
                user_id=user_id,
                book_id=book_id,
                last_chapter_id=chapter_id,
                last_paragraph_id=paragraph_id,
                create_time=now,
                update_time=now,
            )
            db.add(new_item)
        await db.flush()

    @classmethod
    async def get_history_list(cls, db: AsyncSession, user_id: int) -> list[dict[str, Any]]:
        """
        获取用户阅读历史（按时间倒序）

        :param db: orm对象
        :param user_id: 用户ID
        :return: 历史条目字典列表
        """
        rows = (
            await db.execute(
                select(
                    GujiReadHistory.history_id,
                    GujiReadHistory.book_id,
                    GujiBook.book_name,
                    GujiBook.author,
                    GujiReadHistory.chapter_id,
                    GujiChapter.chapter_name,
                    GujiReadHistory.paragraph_id,
                    GujiReadHistory.read_time,
                )
                .join(GujiBook, GujiBook.book_id == GujiReadHistory.book_id)
                .outerjoin(GujiChapter, GujiChapter.chapter_id == GujiReadHistory.chapter_id)
                .where(GujiReadHistory.user_id == user_id)
                .order_by(GujiReadHistory.read_time.desc())
                .limit(50)
            )
        ).all()
        return [dict(row._mapping) for row in rows]

    @classmethod
    async def add_history(
        cls, db: AsyncSession, user_id: int, book_id: int, chapter_id: int, paragraph_id: int
    ) -> None:
        """
        新增阅读历史记录

        :param db: orm对象
        :param user_id: 用户ID
        :param book_id: 书目ID
        :param chapter_id: 章节ID
        :param paragraph_id: 段落ID
        :return: None
        """
        history = GujiReadHistory(
            user_id=user_id,
            book_id=book_id,
            chapter_id=chapter_id,
            paragraph_id=paragraph_id,
            read_time=TimezoneUtil.utc_now(),
        )
        db.add(history)
        await db.flush()

    @classmethod
    async def get_audio_list(cls, db: AsyncSession, book_id: int) -> Sequence[GujiAudio]:
        """
        获取书目听书音频列表

        :param db: orm对象
        :param book_id: 书目ID
        :return: 音频列表
        """
        return (
            (
                await db.execute(
                    select(GujiAudio)
                    .where(GujiAudio.book_id == book_id)
                    .order_by(GujiAudio.audio_id.asc())
                )
            )
            .scalars()
            .all()
        )

    @classmethod
    async def count_book_chapters(cls, db: AsyncSession, book_id: int) -> int:
        """
        统计书目章节数

        :param db: orm对象
        :param book_id: 书目ID
        :return: 章节数
        """
        return (
            await db.execute(select(func.count(GujiChapter.chapter_id)).where(GujiChapter.book_id == book_id))
        ).scalar() or 0
