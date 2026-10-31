"""
识典古籍模块 - 数据库会话依赖

在框架通用会话基础上补充「响应成功后统一提交、异常回滚」，
避免每个写接口都在service层显式commit。
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import DataSourceRegistry
from utils.log_util import logger


async def provide_guji_db_session() -> AsyncIterator[AsyncSession]:
    """
    提供古籍模块数据库会话，响应成功后自动提交

    :return: 异步数据库会话
    """
    async with DataSourceRegistry.session() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            logger.warning(f'古籍模块数据库会话已回滚: {exc}')
            raise


GujiDbSession = Annotated[AsyncSession, Depends(provide_guji_db_session)]
"""
古籍模块数据库会话依赖项
"""
