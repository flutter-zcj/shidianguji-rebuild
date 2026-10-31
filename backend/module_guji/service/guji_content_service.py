"""
识典古籍模块 - 内容域服务层
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_guji.dao.guji_content_dao import GujiContentDao
from module_guji.dao.guji_media_dao import GujiMediaDao
from module_guji.entity.do.guji_content_do import GujiFeedback
from utils.common_util import CamelCaseUtil


class GujiContentService:
    """
    古籍内容域服务层
    """

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
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

    @classmethod
    async def get_book_detail_services(cls, db: AsyncSession, book_id: int, need_catalog: int = 0) -> dict[str, Any]:
        """
        获取书籍详情（含卷、目录）

        :param db: orm对象
        :param book_id: 书籍ID
        :param need_catalog: 是否需要目录
        :return: 书籍详情
        """
        book = await GujiContentDao.get_book_by_id(db, book_id)
        if book is None:
            return {}
        detail = CamelCaseUtil.transform_result(
            {column.name: getattr(book, column.name) for column in book.__table__.columns}
        )
        detail['volumes'] = await GujiContentDao.get_volume_list(db, book_id)
        if need_catalog:
            detail['chapters'] = await GujiContentDao.get_chapter_list(db, book_id)
            detail['bookChapterList'] = detail['chapters']
        return detail

    @classmethod
    async def get_book_list_services(
        cls, db: AsyncSession, keyword: str | None, category: str | None, dynasty: str | None, page_num: int, page_size: int
    ) -> dict[str, Any]:
        """
        获取书籍列表

        :param db: orm对象
        :param keyword: 关键词
        :param category: 分类
        :param dynasty: 朝代
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页结果
        """
        page_result = await GujiContentDao.search_book_list(db, keyword, category, dynasty, page_num, page_size)
        rows = GujiContentDao._rows(page_result.rows)
        return {'rows': rows, 'total': page_result.total, 'pageNum': page_num, 'pageSize': page_size}

    @classmethod
    async def batch_get_book_services(cls, db: AsyncSession, book_ids: list[int]) -> list[dict[str, Any]]:
        """
        批量获取书籍

        :param db: orm对象
        :param book_ids: 书籍ID列表
        :return: 书籍列表
        """
        return await GujiContentDao.get_book_list(db, [cls._safe_int(item) for item in book_ids if str(item).isdigit()])

    @classmethod
    async def get_category_tree_services(cls, db: AsyncSession, cate_type: str | None = None) -> list[dict[str, Any]]:
        """
        获取分类树（组装children）

        :param db: orm对象
        :param cate_type: 分类体系
        :return: 分类树
        """
        categories = await GujiContentDao.get_category_tree(db, cate_type)
        node_map: dict[int, dict[str, Any]] = {}
        for item in categories:
            item['children'] = []
            node_map[item.get('cateId')] = item
        tree: list[dict[str, Any]] = []
        for item in categories:
            parent_id = item.get('parentId') or 0
            parent = node_map.get(parent_id)
            if parent is not None and parent_id != item.get('cateId'):
                parent['children'].append(item)
            else:
                tree.append(item)
        return tree

    @classmethod
    async def get_book_by_category_services(
        cls, db: AsyncSession, cate_id: int | None, page_num: int, page_size: int
    ) -> dict[str, Any]:
        """
        按分类获取书籍

        :param db: orm对象
        :param cate_id: 分类ID
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页结果
        """
        page_result = await GujiContentDao.get_book_list_by_category(db, cate_id, page_num, page_size)
        return {
            'rows': GujiContentDao._rows(page_result.rows),
            'total': page_result.total,
            'pageNum': page_num,
            'pageSize': page_size,
        }

    @classmethod
    async def get_paragraphs_services(
        cls, db: AsyncSession, book_id: int, chapter_id: int | None, page_index: int, page_size: int
    ) -> dict[str, Any]:
        """
        获取阅读器正文段落

        :param db: orm对象
        :param book_id: 书籍ID
        :param chapter_id: 章节ID
        :param page_index: 页码
        :param page_size: 每页条数
        :return: 段落分页结果
        """
        paragraphs, total = await GujiContentDao.get_paragraph_list(db, book_id, chapter_id, page_index, page_size)
        return {'paragraphs': paragraphs, 'totalParaNum': total, 'pageIndex': page_index, 'pageSize': page_size}

    @classmethod
    async def get_chapter_list_services(cls, db: AsyncSession, book_id: int, volume_id: int | None = None) -> dict[str, Any]:
        """
        获取章节目录

        :param db: orm对象
        :param book_id: 书籍ID
        :param volume_id: 卷ID
        :return: 目录结果
        """
        chapters = await GujiContentDao.get_chapter_list(db, book_id, volume_id)
        return {'chapters': chapters, 'bookChapterList': chapters, 'total': len(chapters)}

    @classmethod
    async def get_volume_detail_services(cls, db: AsyncSession, volume_id: int) -> dict[str, Any]:
        """
        获取卷详情

        :param db: orm对象
        :param volume_id: 卷ID
        :return: 卷详情
        """
        volume = await GujiContentDao.get_volume_by_id(db, volume_id)
        if volume is None:
            return {}
        return CamelCaseUtil.transform_result(
            {column.name: getattr(volume, column.name) for column in volume.__table__.columns}
        )

    @classmethod
    async def search_book_services(cls, db: AsyncSession, keyword: str, page_num: int, page_size: int) -> dict[str, Any]:
        """
        搜索书籍

        :param db: orm对象
        :param keyword: 检索词
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 检索结果
        """
        return await cls.get_book_list_services(db, keyword, None, None, page_num, page_size)

    @classmethod
    async def search_paragraph_services(
        cls, db: AsyncSession, keyword: str, book_id: int | None, page_num: int, page_size: int
    ) -> dict[str, Any]:
        """
        全文检索段落

        :param db: orm对象
        :param keyword: 检索词
        :param book_id: 限定书籍
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 检索结果
        """
        page_result = await GujiContentDao.search_paragraph_list(db, keyword, book_id, page_num, page_size)
        rows = GujiContentDao._rows(page_result.rows)
        for row in rows:
            row['highlight'] = keyword
        return {'rows': rows, 'total': page_result.total, 'pageNum': page_num, 'pageSize': page_size}

    @classmethod
    async def get_contributor_services(
        cls, db: AsyncSession, book_id: int, contributor_type: str, page_num: int, page_size: int
    ) -> dict[str, Any]:
        """
        获取贡献者/勘误者

        :param db: orm对象
        :param book_id: 书籍ID
        :param contributor_type: 类型
        :param page_num: 页码
        :param page_size: 每页条数
        :return: 分页结果
        """
        page_result = await GujiContentDao.get_contributor_list(db, book_id, contributor_type, page_num, page_size)
        rows = GujiContentDao._rows(page_result.rows)
        return {'contributorList': rows, 'total': page_result.total, 'hasMore': page_result.total > page_num * page_size}

    @classmethod
    async def get_quotation_list_services(
        cls,
        db: AsyncSession,
        user_id: int,
        book_id: int | None,
        cate_id: int | None,
        keyword: str | None,
        offset: int,
        page_size: int,
    ) -> dict[str, Any]:
        """
        获取名句列表（带收藏态）

        :param db: orm对象
        :param user_id: 用户ID
        :param book_id: 书籍ID
        :param cate_id: 分类ID
        :param keyword: 关键词
        :param offset: 偏移量
        :param page_size: 每页条数
        :return: 名句列表
        """
        from module_guji.dao.guji_user_dao import GujiUserDao

        rows, total = await GujiContentDao.get_quotation_list(db, book_id, cate_id, keyword, offset, page_size)
        biz_ids = [str(row.get('quotationId')) for row in rows]
        favorite_map = await GujiUserDao.check_favorite(db, user_id, biz_ids, 'quotation')
        for row in rows:
            row['isFavorite'] = favorite_map.get(str(row.get('quotationId')), 0)
        next_offset = offset + len(rows)
        return {
            'rows': rows,
            'total': total,
            'nextPageToken': str(next_offset) if next_offset < total else None,
            'hasMore': next_offset < total,
        }

    @classmethod
    async def get_quotation_detail_services(cls, db: AsyncSession, quotation_id: int) -> dict[str, Any]:
        """
        获取名句详情

        :param db: orm对象
        :param quotation_id: 名句ID
        :return: 名句详情
        """
        quotation = await GujiContentDao.get_quotation_by_id(db, quotation_id)
        if quotation is None:
            return {}
        return CamelCaseUtil.transform_result(
            {column.name: getattr(quotation, column.name) for column in quotation.__table__.columns}
        )

    @classmethod
    async def get_quotation_category_services(cls, db: AsyncSession) -> dict[str, Any]:
        """
        获取名句分类

        :param db: orm对象
        :return: 分类列表
        """
        categories = await GujiContentDao.get_quotation_category_list(db)
        return {'rows': categories, 'total': len(categories)}

    @classmethod
    async def get_dictionary_services(cls, db: AsyncSession, word: str) -> dict[str, Any]:
        """
        查字（词典释义聚合）

        :param db: orm对象
        :param word: 查询词
        :return: 释义结果
        """
        if not word:
            return {}
        char = word[:1]
        dict_char = await GujiContentDao.get_dict_char(db, char)
        if dict_char is None:
            return {'word': word, 'dictionaryExplain': {}}
        import json

        def _load(value: str | None) -> Any:
            if not value:
                return None
            try:
                return json.loads(value)
            except (ValueError, TypeError):
                return value

        return {
            'word': word,
            'char': dict_char.char,
            'pinyin': dict_char.pinyin,
            'rad': dict_char.rad,
            'polyphone': dict_char.polyphone,
            'explain': dict_char.explain,
            'dictionaryExplain': {
                'hanyuDoc': _load(dict_char.hanyu_doc),
                'kangxiDocs': _load(dict_char.kangxi_docs),
                'shuowenjieziDoc': _load(dict_char.shuowenjiezi_doc),
            },
        }

    @classmethod
    async def get_entity_services(cls, db: AsyncSession, entity_id: int) -> dict[str, Any]:
        """
        获取实体详情

        :param db: orm对象
        :param entity_id: 实体ID
        :return: 实体详情
        """
        entity = await GujiContentDao.get_entity_by_id(db, entity_id)
        if entity is None:
            return {}
        return CamelCaseUtil.transform_result(
            {column.name: getattr(entity, column.name) for column in entity.__table__.columns}
        )

    @classmethod
    async def get_margin_note_services(cls, db: AsyncSession, margin_note_ids: list[int]) -> dict[str, Any]:
        """
        批量获取页边注

        :param db: orm对象
        :param margin_note_ids: 页边注ID列表
        :return: 页边注列表
        """
        rows = await GujiContentDao.get_margin_note_list(db, margin_note_ids)
        return {'marginNoteList': rows, 'total': len(rows)}

    @classmethod
    async def add_feedback_services(cls, db: AsyncSession, user_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        新增内容勘误反馈

        :param db: orm对象
        :param user_id: 用户ID
        :param data: 反馈内容
        :return: 反馈结果
        """
        feedback = GujiFeedback(
            user_id=user_id,
            book_id=cls._safe_int(data.get('bookId')),
            issue=data.get('issue'),
            quote=data.get('quote'),
            email=data.get('email'),
            issue_type=data.get('issueType'),
            description=data.get('description'),
            translate_issue=data.get('translateIssue'),
            issue_ori=data.get('issueOri'),
            cus_description=data.get('cusDescription'),
        )
        await GujiContentDao.add_feedback(db, feedback)
        return {'feedbackId': feedback.feedback_id}

    @classmethod
    async def get_homepage_services(cls, db: AsyncSession, user_id: int) -> dict[str, Any]:
        """
        获取首页聚合数据（Banner + 推荐板块）

        :param db: orm对象
        :param user_id: 用户ID
        :return: 首页数据
        """
        banner_list = await GujiMediaDao.get_banner_list(db)
        recommend_list = await GujiMediaDao.get_recommend_list(db, None, None)
        modules: dict[str, dict[str, Any]] = {}
        for item in recommend_list:
            module_key = item.get('moduleKey') or 'recommend'
            module = modules.setdefault(
                module_key, {'moduleKey': module_key, 'moduleTitle': item.get('moduleTitle'), 'items': []}
            )
            module['items'].append(item)
        return {
            'bannerList': banner_list,
            'modules': list(modules.values()),
            'recommendList': recommend_list,
        }
