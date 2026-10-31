"""
识典古籍模块 - 内容域数据库操作层
"""

from typing import Any

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_guji.entity.do.guji_content_do import (
    GujiBook,
    GujiCategory,
    GujiChapter,
    GujiContributor,
    GujiDictChar,
    GujiEntity,
    GujiEntityRef,
    GujiFeedback,
    GujiMarginNote,
    GujiParagraph,
    GujiQuotation,
    GujiQuotationCategory,
    GujiVolume,
)
from utils.common_util import CamelCaseUtil
from utils.page_util import PageUtil


class GujiContentDao:
    """
    古籍内容域数据库操作层
    """

    @classmethod
    def _rows(cls, result: Any) -> list[dict[str, Any]]:
        """
        将ORM查询结果转换为驼峰字典列表

        :param result: 查询结果
        :return: 驼峰字典列表
        """
        items = list(result)
        if not items:
            return []
        if isinstance(items[0], dict):
            return [CamelCaseUtil.transform_result(item) for item in items]
        rows = []
        for item in items:
            if isinstance(item, (list, tuple)):
                item = item[0]  # noqa: PLW2901
            row = {}
            for column in item.__table__.columns:
                row[column.name] = getattr(item, column.name)
            rows.append(CamelCaseUtil.transform_result(row))
        return rows

    # ------------------------------ 书籍 ------------------------------

    @classmethod
    async def get_book_by_id(cls, db: AsyncSession, book_id: int) -> GujiBook | None:
        """
        根据书籍ID获取书籍

        :param db: orm对象
        :param book_id: 书籍ID
        :return: 书籍对象
        """
        return (await db.execute(select(GujiBook).where(GujiBook.book_id == book_id))).scalars().first()

    @classmethod
    async def get_book_list(cls, db: AsyncSession, book_ids: list[int]) -> list[dict[str, Any]]:
        """
        批量获取书籍

        :param db: orm对象
        :param book_ids: 书籍ID列表
        :return: 书籍列表
        """
        if not book_ids:
            return []
        result = (
            await db.execute(select(GujiBook).where(GujiBook.book_id.in_(book_ids), GujiBook.del_flag == '0'))
        ).scalars().all()
        return cls._rows(result)

    @classmethod
    async def search_book_list(
        cls, db: AsyncSession, keyword: str | None, category: str | None, dynasty: str | None, page_num: int, page_size: int
    ) -> Any:
        """
        搜索/筛选书籍列表

        :param db: orm对象
        :param keyword: 关键词
        :param category: 传统分类
        :param dynasty: 朝代
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        keyword_like = f'%{keyword}%' if keyword else None
        query = (
            select(GujiBook)
            .where(
                GujiBook.del_flag == '0',
                or_(
                    GujiBook.book_name.like(keyword_like),
                    GujiBook.authors.like(keyword_like),
                    GujiBook.abstract.like(keyword_like),
                    GujiBook.add_names.like(keyword_like),
                )
                if keyword_like
                else True,
                GujiBook.traditional_category == category if category else True,
                GujiBook.dynasty_category_name == dynasty if dynasty else True,
            )
            .order_by(GujiBook.popularity.desc(), GujiBook.book_id.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def count_book(cls, db: AsyncSession) -> int:
        """
        统计书籍总数

        :param db: orm对象
        :return: 书籍总数
        """
        return (await db.execute(select(func.count()).select_from(GujiBook).where(GujiBook.del_flag == '0'))).scalar_one()

    @classmethod
    async def count_volume_version(cls, db: AsyncSession, volume_id: int | None, version: str | None) -> int:
        """
        统计卷版本数量（阅读器用于校验版本一致性）

        :param db: orm对象
        :param volume_id: 卷ID
        :param version: 版本
        :return: 数量
        """
        return (
            await db.execute(
                select(func.count())
                .select_from(GujiVolume)
                .where(GujiVolume.volume_id == volume_id if volume_id else True, GujiVolume.del_flag == '0')
            )
        ).scalar_one()

    # ------------------------------ 卷 / 章节 / 段落 ------------------------------

    @classmethod
    async def get_volume_by_id(cls, db: AsyncSession, volume_id: int) -> GujiVolume | None:
        """
        根据卷ID获取卷

        :param db: orm对象
        :param volume_id: 卷ID
        :return: 卷对象
        """
        return (await db.execute(select(GujiVolume).where(GujiVolume.volume_id == volume_id))).scalars().first()

    @classmethod
    async def get_volume_list(cls, db: AsyncSession, book_id: int) -> list[dict[str, Any]]:
        """
        获取书籍的卷列表

        :param db: orm对象
        :param book_id: 书籍ID
        :return: 卷列表
        """
        result = (
            await db.execute(
                select(GujiVolume)
                .where(GujiVolume.book_id == book_id, GujiVolume.del_flag == '0')
                .order_by(GujiVolume.volume_order, GujiVolume.volume_id)
            )
        ).scalars().all()
        return cls._rows(result)

    @classmethod
    async def get_chapter_list(cls, db: AsyncSession, book_id: int, volume_id: int | None = None) -> list[dict[str, Any]]:
        """
        获取章节目录

        :param db: orm对象
        :param book_id: 书籍ID
        :param volume_id: 卷ID
        :return: 章节列表
        """
        result = (
            await db.execute(
                select(GujiChapter)
                .where(
                    GujiChapter.book_id == book_id,
                    GujiChapter.volume_id == volume_id if volume_id else True,
                    GujiChapter.del_flag == '0',
                )
                .order_by(GujiChapter.chapter_order, GujiChapter.chapter_id)
            )
        ).scalars().all()
        return cls._rows(result)

    @classmethod
    async def get_chapter_by_id(cls, db: AsyncSession, chapter_id: int) -> GujiChapter | None:
        """
        根据章节ID获取章节

        :param db: orm对象
        :param chapter_id: 章节ID
        :return: 章节对象
        """
        return (await db.execute(select(GujiChapter).where(GujiChapter.chapter_id == chapter_id))).scalars().first()

    @classmethod
    async def get_paragraph_count(cls, db: AsyncSession, chapter_id: int) -> int:
        """
        统计章节段落数量

        :param db: orm对象
        :param chapter_id: 章节ID
        :return: 段落数量
        """
        return (
            await db.execute(
                select(func.count())
                .select_from(GujiParagraph)
                .where(GujiParagraph.chapter_id == chapter_id, GujiParagraph.del_flag == '0')
            )
        ).scalar_one()

    @classmethod
    async def get_paragraph_list(
        cls, db: AsyncSession, book_id: int, chapter_id: int | None, page_index: int, page_size: int
    ) -> tuple[list[dict[str, Any]], int]:
        """
        获取章节段落列表（阅读器正文）

        :param db: orm对象
        :param book_id: 书籍ID
        :param chapter_id: 章节ID
        :param page_index: 页码（从1开始）
        :param page_size: 每页段落数
        :return: 段落列表与总数
        """
        conditions: list[ColumnElement[bool]] = [GujiParagraph.del_flag == '0']
        if book_id:
            conditions.append(GujiParagraph.book_id == book_id)
        if chapter_id:
            conditions.append(GujiParagraph.chapter_id == chapter_id)
        total = (await db.execute(select(func.count()).select_from(GujiParagraph).where(*conditions))).scalar_one()
        offset = max(page_index - 1, 0) * page_size
        result = (
            await db.execute(
                select(GujiParagraph)
                .where(*conditions)
                .order_by(GujiParagraph.para_index, GujiParagraph.paragraph_id)
                .offset(offset)
                .limit(page_size)
            )
        ).scalars().all()
        return cls._rows(result), total

    @classmethod
    async def search_paragraph_list(
        cls, db: AsyncSession, keyword: str, book_id: int | None, page_num: int, page_size: int
    ) -> Any:
        """
        全文检索段落

        :param db: orm对象
        :param keyword: 检索词
        :param book_id: 限定书籍ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        keyword_like = f'%{keyword}%' if keyword else None
        query = (
            select(GujiParagraph)
            .where(
                GujiParagraph.del_flag == '0',
                GujiParagraph.book_id == book_id if book_id else True,
                or_(
                    GujiParagraph.content.like(keyword_like),
                    GujiParagraph.translation.like(keyword_like),
                    GujiParagraph.chapter_name.like(keyword_like),
                )
                if keyword_like
                else True,
            )
            .order_by(GujiParagraph.paragraph_id)
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    # ------------------------------ 分类 ------------------------------

    @classmethod
    async def get_category_tree(cls, db: AsyncSession, cate_type: str | None = None) -> list[dict[str, Any]]:
        """
        获取分类树

        :param db: orm对象
        :param cate_type: 分类体系
        :return: 分类列表
        """
        result = (
            await db.execute(
                select(GujiCategory)
                .where(
                    GujiCategory.del_flag == '0',
                    GujiCategory.cate_type == cate_type if cate_type else True,
                )
                .order_by(GujiCategory.order_num, GujiCategory.cate_id)
            )
        ).scalars().all()
        return cls._rows(result)

    @classmethod
    async def get_book_list_by_category(
        cls, db: AsyncSession, cate_id: int | None, page_num: int, page_size: int
    ) -> Any:
        """
        按分类获取书籍列表

        :param db: orm对象
        :param cate_id: 分类ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        conditions: list[ColumnElement] = [GujiBook.del_flag == '0']
        if cate_id:
            # 分类ID -> 分类名（经/史/子/集），书籍表存的是传统四部名称
            cate_name = (
                await db.execute(select(GujiCategory.cate_name).where(GujiCategory.cate_id == cate_id))
            ).scalar()
            conditions.append(
                or_(
                    GujiBook.traditional_category == cate_name if cate_name else GujiBook.traditional_category == str(cate_id),
                    GujiBook.traditional_category == str(cate_id),
                )
            )
        query = (
            select(GujiBook)
            .where(*conditions)
            .order_by(GujiBook.popularity.desc(), GujiBook.book_id.desc())
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    # ------------------------------ 贡献者 ------------------------------

    @classmethod
    async def get_contributor_list(
        cls, db: AsyncSession, book_id: int, contributor_type: str, page_num: int, page_size: int
    ) -> Any:
        """
        获取书籍贡献者/勘误者列表

        :param db: orm对象
        :param book_id: 书籍ID
        :param contributor_type: contributor/corrector
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiContributor)
            .where(
                GujiContributor.book_id == book_id,
                GujiContributor.contributor_type == contributor_type,
                GujiContributor.del_flag == '0',
            )
            .order_by(GujiContributor.contribution_count.desc(), GujiContributor.order_num)
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    # ------------------------------ 名句 ------------------------------

    @classmethod
    async def get_quotation_list(
        cls,
        db: AsyncSession,
        book_id: int | None,
        cate_id: int | None,
        keyword: str | None,
        offset: int,
        page_size: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        获取名句列表（游标分页）

        :param db: orm对象
        :param book_id: 书籍ID
        :param cate_id: 分类ID
        :param keyword: 关键词
        :param offset: 偏移量
        :param page_size: 每页条数
        :return: 名句列表与总数
        """
        keyword_like = f'%{keyword}%' if keyword else None
        conditions: list[ColumnElement[bool]] = [GujiQuotation.del_flag == '0']
        if book_id:
            conditions.append(GujiQuotation.book_id == book_id)
        if cate_id:
            conditions.append(GujiQuotation.cate_id == cate_id)
        if keyword_like:
            conditions.append(or_(GujiQuotation.famous_quote.like(keyword_like), GujiQuotation.author.like(keyword_like)))
        total = (await db.execute(select(func.count()).select_from(GujiQuotation).where(*conditions))).scalar_one()
        result = (
            await db.execute(
                select(GujiQuotation)
                .where(*conditions)
                .order_by(GujiQuotation.favorites_num.desc(), GujiQuotation.quotation_id)
                .offset(offset)
                .limit(page_size)
            )
        ).scalars().all()
        return cls._rows(result), total

    @classmethod
    async def get_quotation_by_id(cls, db: AsyncSession, quotation_id: int) -> GujiQuotation | None:
        """
        根据名句ID获取名句

        :param db: orm对象
        :param quotation_id: 名句ID
        :return: 名句对象
        """
        return (await db.execute(select(GujiQuotation).where(GujiQuotation.quotation_id == quotation_id))).scalars().first()

    @classmethod
    async def get_quotation_category_list(cls, db: AsyncSession) -> list[dict[str, Any]]:
        """
        获取名句分类列表

        :param db: orm对象
        :return: 分类列表
        """
        result = (
            await db.execute(
                select(GujiQuotationCategory)
                .where(GujiQuotationCategory.del_flag == '0')
                .order_by(GujiQuotationCategory.order_num)
            )
        ).scalars().all()
        return cls._rows(result)

    # ------------------------------ 实体 / 字典 ------------------------------

    @classmethod
    async def get_entity_by_id(cls, db: AsyncSession, entity_id: int) -> GujiEntity | None:
        """
        根据实体ID获取实体

        :param db: orm对象
        :param entity_id: 实体ID
        :return: 实体对象
        """
        return (await db.execute(select(GujiEntity).where(GujiEntity.entity_id == entity_id))).scalars().first()

    @classmethod
    async def search_entity_list(cls, db: AsyncSession, keyword: str | None, page_num: int, page_size: int) -> Any:
        """
        搜索实体

        :param db: orm对象
        :param keyword: 关键词
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiEntity)
            .where(
                GujiEntity.del_flag == '0',
                GujiEntity.normal_name.like(f'%{keyword}%') if keyword else True,
            )
            .order_by(GujiEntity.entity_id)
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def get_entity_ref_list(cls, db: AsyncSession, entity_ids: list[int]) -> list[dict[str, Any]]:
        """
        批量获取实体引用

        :param db: orm对象
        :param entity_ids: 实体ID列表
        :return: 引用列表
        """
        if not entity_ids:
            return []
        result = (
            await db.execute(
                select(GujiEntityRef).where(GujiEntityRef.entity_id.in_(entity_ids), GujiEntityRef.del_flag == '0')
            )
        ).scalars().all()
        return cls._rows(result)

    @classmethod
    async def get_dict_char(cls, db: AsyncSession, char: str) -> GujiDictChar | None:
        """
        查询单字字典详情

        :param db: orm对象
        :param char: 汉字
        :return: 字形对象
        """
        return (await db.execute(select(GujiDictChar).where(GujiDictChar.char == char))).scalars().first()

    @classmethod
    async def search_dict_char_by_rad(cls, db: AsyncSession, rad: str | None, page_num: int, page_size: int) -> Any:
        """
        按部首检字

        :param db: orm对象
        :param rad: 部首
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页对象
        """
        query = (
            select(GujiDictChar)
            .where(GujiDictChar.del_flag == '0', GujiDictChar.rad == rad if rad else True)
            .order_by(GujiDictChar.char_id)
        )
        return await PageUtil.paginate(db, query, page_num, page_size, True)

    @classmethod
    async def get_dict_char_list(cls, db: AsyncSession, char_ids: list[str]) -> list[dict[str, Any]]:
        """
        批量获取字形

        :param db: orm对象
        :param char_ids: 字形ID列表
        :return: 字形列表
        """
        if not char_ids:
            return []
        int_ids = [int(item) for item in char_ids if str(item).isdigit()]
        if not int_ids:
            chars = (
                await db.execute(select(GujiDictChar).where(GujiDictChar.char.in_(char_ids)))
            ).scalars().all()
            return cls._rows(chars)
        result = (await db.execute(select(GujiDictChar).where(GujiDictChar.char_id.in_(int_ids)))).scalars().all()
        return cls._rows(result)

    # ------------------------------ 页边注 / 反馈 ------------------------------

    @classmethod
    async def get_margin_note_list(cls, db: AsyncSession, margin_note_ids: list[int]) -> list[dict[str, Any]]:
        """
        批量获取页边注

        :param db: orm对象
        :param margin_note_ids: 页边注ID列表
        :return: 页边注列表
        """
        if not margin_note_ids:
            return []
        result = (
            await db.execute(
                select(GujiMarginNote).where(
                    GujiMarginNote.margin_note_id.in_(margin_note_ids), GujiMarginNote.del_flag == '0'
                )
            )
        ).scalars().all()
        return cls._rows(result)

    @classmethod
    async def get_margin_note_by_id(cls, db: AsyncSession, margin_note_id: int) -> GujiMarginNote | None:
        """
        获取页边注详情

        :param db: orm对象
        :param margin_note_id: 页边注ID
        :return: 页边注对象
        """
        return (
            await db.execute(select(GujiMarginNote).where(GujiMarginNote.margin_note_id == margin_note_id))
        ).scalars().first()

    @classmethod
    async def add_feedback(cls, db: AsyncSession, feedback: GujiFeedback) -> GujiFeedback:
        """
        新增勘误反馈

        :param db: orm对象
        :param feedback: 反馈对象
        :return: 反馈对象
        """
        db.add(feedback)
        await db.flush()
        return feedback
