from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_guji.dao.guji_dao import GujiDao
from module_guji.entity.vo.guji_vo import (
    GujiAudioModel,
    GujiBookModel,
    GujiBookPageQueryModel,
    GujiBookshelfAddModel,
    GujiBookshelfModel,
    GujiChapterModel,
    GujiHistoryModel,
    GujiParagraphPageQueryModel,
    GujiReadHistoryModel,
)
from utils.common_util import CamelCaseUtil


class GujiService:
    """
    古籍阅读平台服务层
    """

    @classmethod
    async def get_book_list_services(
        cls, query_db: AsyncSession, query_object: GujiBookPageQueryModel
    ) -> PageModel | list[dict[str, Any]]:
        """
        获取古籍书目分页列表

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :return: 书目分页结果
        """
        result = await GujiDao.get_book_list(query_db, query_object, is_page=True)
        if isinstance(result, PageModel):
            result.rows = [GujiBookModel(**CamelCaseUtil.transform_result(row)) for row in result.rows]
        return result

    @classmethod
    async def get_book_detail_services(cls, query_db: AsyncSession, book_id: int) -> GujiBookModel:
        """
        获取古籍书目详情

        :param query_db: orm对象
        :param book_id: 书目ID
        :return: 书目详情模型
        """
        book = await GujiDao.get_book_detail(query_db, book_id)
        if not book:
            raise ServiceException(message=f'书目 {book_id} 不存在或已下架')
        return GujiBookModel(**CamelCaseUtil.transform_result(book))

    @classmethod
    async def get_chapter_list_services(cls, query_db: AsyncSession, book_id: int) -> list[GujiChapterModel]:
        """
        获取书目章节目录

        :param query_db: orm对象
        :param book_id: 书目ID
        :return: 章节列表
        """
        book = await GujiDao.get_book_detail(query_db, book_id)
        if not book:
            raise ServiceException(message=f'书目 {book_id} 不存在或已下架')
        chapters = await GujiDao.get_chapter_list(query_db, book_id)
        return [GujiChapterModel(**CamelCaseUtil.transform_result(chapter)) for chapter in chapters]

    @classmethod
    async def get_paragraph_page_services(
        cls, query_db: AsyncSession, query_object: GujiParagraphPageQueryModel
    ) -> PageModel:
        """
        获取章节段落分页

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :return: 段落分页结果
        """
        result = await GujiDao.get_paragraph_page(query_db, query_object, is_page=True)
        if isinstance(result, PageModel):
            result.rows = [CamelCaseUtil.transform_result(row) for row in result.rows]
        return result

    @classmethod
    async def get_bookshelf_list_services(cls, query_db: AsyncSession, user_id: int) -> list[GujiBookshelfModel]:
        """
        获取用户书架列表

        :param query_db: orm对象
        :param user_id: 用户ID
        :return: 书架条目列表
        """
        rows = await GujiDao.get_bookshelf_list(query_db, user_id)
        return [GujiBookshelfModel(**CamelCaseUtil.transform_result(row)) for row in rows]

    @classmethod
    async def add_bookshelf_services(
        cls, query_db: AsyncSession, user_id: int, add_object: GujiBookshelfAddModel
    ) -> CrudResponseModel:
        """
        加入书架

        :param query_db: orm对象
        :param user_id: 用户ID
        :param add_object: 加入书架参数对象
        :return: 操作结果
        """
        book = await GujiDao.get_book_detail(query_db, add_object.book_id)
        if not book:
            raise ServiceException(message=f'书目 {add_object.book_id} 不存在或已下架')
        await GujiDao.add_bookshelf(query_db, user_id, add_object.book_id)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='加入书架成功')

    @classmethod
    async def delete_bookshelf_services(cls, query_db: AsyncSession, user_id: int, book_id: int) -> CrudResponseModel:
        """
        移出书架

        :param query_db: orm对象
        :param user_id: 用户ID
        :param book_id: 书目ID
        :return: 操作结果
        """
        await GujiDao.delete_bookshelf(query_db, user_id, book_id)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='移出书架成功')

    @classmethod
    async def get_history_list_services(cls, query_db: AsyncSession, user_id: int) -> list[GujiHistoryModel]:
        """
        获取用户阅读历史

        :param query_db: orm对象
        :param user_id: 用户ID
        :return: 历史条目列表
        """
        rows = await GujiDao.get_history_list(query_db, user_id)
        return [GujiHistoryModel(**CamelCaseUtil.transform_result(row)) for row in rows]

    @classmethod
    async def add_history_services(
        cls, query_db: AsyncSession, user_id: int, history_object: GujiReadHistoryModel
    ) -> CrudResponseModel:
        """
        上报阅读进度（写历史 + 更新书架进度）

        :param query_db: orm对象
        :param user_id: 用户ID
        :param history_object: 阅读进度参数对象
        :return: 操作结果
        """
        book = await GujiDao.get_book_detail(query_db, history_object.book_id)
        if not book:
            raise ServiceException(message=f'书目 {history_object.book_id} 不存在或已下架')
        await GujiDao.add_history(
            query_db,
            user_id,
            history_object.book_id,
            history_object.chapter_id,
            history_object.paragraph_id,
        )
        await GujiDao.update_bookshelf_progress(
            query_db,
            user_id,
            history_object.book_id,
            history_object.chapter_id,
            history_object.paragraph_id,
        )
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='阅读进度已同步')

    @classmethod
    async def get_audio_list_services(cls, query_db: AsyncSession, book_id: int) -> list[GujiAudioModel]:
        """
        获取书目听书音频列表

        :param query_db: orm对象
        :param book_id: 书目ID
        :return: 音频列表
        """
        audios = await GujiDao.get_audio_list(query_db, book_id)
        return [GujiAudioModel(**CamelCaseUtil.transform_result(audio)) for audio in audios]
