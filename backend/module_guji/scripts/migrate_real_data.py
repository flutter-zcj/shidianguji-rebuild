"""
识典古籍：把既有古籍库（gj_category / gj_book / gj_chapter）的真实数据迁入 guji_* 表

用法（在 ruoyi-fastapi-backend 目录下执行）：
    python -m module_guji.scripts.migrate_real_data

可选参数：
    --sql <路径>   指定迁移 SQL（默认与本脚本同目录的 migrate_real_data.sql）
    --no-create    只跑 SQL，不建表

流程：
1. 建表（module_guji 全部实体）
2. 执行 migrate_real_data.sql（纯 SQL 迁移，避免 Python 逐行插入百万次往返）
3. 打印迁移结果统计
"""

import argparse
import asyncio
import os

from sqlalchemy import text

from config.database import Base, DataSourceRegistry
from module_guji.dao.guji_content_dao import GujiContentDao  # noqa: F401  触发 DO 注册
from module_guji.dao.guji_media_dao import GujiMediaDao  # noqa: F401
from module_guji.dao.guji_user_dao import GujiUserDao  # noqa: F401

DEFAULT_SQL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrate_real_data.sql')

COUNT_QUERIES = [
    ('分类', 'select count(*) from guji_category'),
    ('书籍', 'select count(*) from guji_book'),
    ('卷', 'select count(*) from guji_volume'),
    ('章节', 'select count(*) from guji_chapter'),
    ('段落', 'select count(*) from guji_paragraph'),
    ('名句', 'select count(*) from guji_quotation'),
    ('推荐位', 'select count(*) from guji_recommend'),
    ('横幅', 'select count(*) from guji_homepage_banner'),
]


async def create_tables() -> None:
    """
    创建古籍模块全部数据表

    :return:
    """
    async with DataSourceRegistry.connection() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.commit()
    print('数据表创建完成')


async def run_migration(sql_path: str) -> None:
    """
    执行迁移 SQL

    :param sql_path: SQL 文件路径
    :return:
    """
    with open(sql_path, encoding='utf-8') as fp:
        sql = fp.read()
    async with DataSourceRegistry.session() as session:
        await session.execute(text(sql))
        await session.commit()
    print(f'迁移 SQL 执行完成：{sql_path}')


async def report() -> None:
    """
    打印迁移结果统计

    :return:
    """
    async with DataSourceRegistry.session() as session:
        print('--- 迁移结果 ---')
        for label, query in COUNT_QUERIES:
            value = (await session.execute(text(query))).scalar_one()
            print(f'{label}: {value}')


async def main() -> None:
    """
    迁移入口

    :return:
    """
    parser = argparse.ArgumentParser(description='识典古籍真实数据迁移')
    parser.add_argument('--sql', default=DEFAULT_SQL, help='迁移 SQL 路径')
    parser.add_argument('--no-create', action='store_true', help='跳过建表')
    args = parser.parse_args()

    await DataSourceRegistry.initialize(log_enabled=False)
    if not args.no_create:
        await create_tables()
    await run_migration(args.sql)
    await report()
    print('识典古籍真实数据迁移完成')


if __name__ == '__main__':
    asyncio.run(main())
