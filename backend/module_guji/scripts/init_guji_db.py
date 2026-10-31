"""
识典古籍模块初始化脚本

用法（在 ruoyi-fastapi-backend 目录下执行）：
    python -m module_guji.scripts.init_guji_db

功能：
1. 建表（module_guji 全部实体）
2. 写入示例数据（书籍、卷、章节、段落、分类、名句、音频、视频、课程、Banner、推荐位）
"""

import asyncio
import json

from sqlalchemy.ext.asyncio import AsyncSession

from config.database import Base
from module_guji.dao.guji_content_dao import GujiContentDao
from module_guji.dao.guji_media_dao import GujiMediaDao
from module_guji.entity.do import guji_content_do as content_do  # noqa: F401
from module_guji.entity.do import guji_media_do as media_do  # noqa: F401
from module_guji.entity.do import guji_user_do as user_do  # noqa: F401

SAMPLE_BOOKS = [
    {
        'book_name': '论语',
        'authors': '孔子弟子及再传弟子',
        'dynasty_category_name': '先秦',
        'dynasty_name': '春秋',
        'traditional_category': '经',
        'importance_level': 10,
        'popularity': 9999,
        'abstract': '儒家经典之一，记录孔子及其弟子言行。',
        'introduction': '《论语》由孔子弟子及再传弟子编纂，是研究孔子思想最重要的文献。',
        'edition': '通行本',
        'library': '识典古籍',
        'is_listening_supported': 1,
        'is_podcast_supported': 1,
    },
    {
        'book_name': '道德经',
        'authors': '老子',
        'dynasty_category_name': '先秦',
        'dynasty_name': '春秋',
        'traditional_category': '子',
        'importance_level': 10,
        'popularity': 9600,
        'abstract': '道家思想的奠基之作，又称《老子》。',
        'introduction': '《道德经》五千余言，分道经与德经两篇。',
        'edition': '王弼本',
        'library': '识典古籍',
        'is_listening_supported': 1,
        'is_podcast_supported': 0,
    },
    {
        'book_name': '史记',
        'authors': '司马迁',
        'dynasty_category_name': '汉',
        'dynasty_name': '西汉',
        'traditional_category': '史',
        'importance_level': 10,
        'popularity': 9400,
        'abstract': '中国第一部纪传体通史。',
        'introduction': '《史记》记载上起黄帝下至汉武帝三千余年历史。',
        'edition': '中华书局点校本',
        'library': '识典古籍',
        'is_listening_supported': 1,
        'is_podcast_supported': 1,
    },
    {
        'book_name': '陶渊明集',
        'authors': '陶渊明',
        'dynasty_category_name': '魏晋',
        'dynasty_name': '东晋',
        'traditional_category': '集',
        'importance_level': 8,
        'popularity': 8200,
        'abstract': '东晋诗人陶渊明诗文总集。',
        'introduction': '收录陶渊明诗、赋、辞、记等作品。',
        'edition': '汲古阁本',
        'library': '识典古籍',
        'is_listening_supported': 1,
        'is_podcast_supported': 0,
    },
]

SAMPLE_CHAPTERS = {
    '论语': ['学而第一', '为政第二', '八佾第三', '里仁第四'],
    '道德经': ['道经上', '道经下', '德经上', '德经下'],
    '史记': ['五帝本纪', '夏本纪', '殷本纪', '周本纪'],
    '陶渊明集': ['归园田居', '饮酒', '桃花源记', '归去来兮辞'],
}

SAMPLE_PARAGRAPHS = [
    ('子曰：“学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知而不愠，不亦君子乎？”',
     '孔子说：“学习了并按时温习，不也很愉快吗？有志同道合的人从远方来，不也很快乐吗？别人不了解自己而不恼怒，不也是君子吗？”',
     '学而：篇名，取首章前两字。'),
    ('子曰：“温故而知新，可以为师矣。”', '孔子说：“温习旧知识而能有新的领悟，就可以做老师了。”', '温故：复习旧学。'),
    ('道可道，非常道；名可名，非常名。', '可以用言语说出来的道，不是恒常的道；可以叫得出来的名，不是恒常的名。', '道：宇宙本原。'),
    ('上善若水。水善利万物而不争，处众人之所恶，故几于道。',
     '最高尚的善像水一样。水善于滋养万物而不与万物相争，停留在众人厌恶的地方，所以最接近道。', '几：接近。'),
]

SAMPLE_QUOTATIONS = [
    ('学而时习之，不亦说乎', '论语', '孔子', '先秦', '励志'),
    ('上善若水，水善利万物而不争', '道德经', '老子', '先秦', '处世'),
    ('究天人之际，通古今之变', '史记', '司马迁', '汉', '治学'),
    ('采菊东篱下，悠然见南山', '陶渊明集', '陶渊明', '魏晋', '田园'),
]


async def _create_tables(engine) -> None:
    """
    创建古籍模块全部数据表

    :param engine: 数据库引擎
    :return:
    """
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def _seed(db: AsyncSession) -> None:
    """
    写入示例数据

    :param db: 数据库会话
    :return:
    """
    # 分类
    for name in ['经', '史', '子', '集']:
        exists = (await db.execute(select_category(name))).scalars().first()
        if exists is None:
            db.add(content_do.GujiCategory(cate_name=name, cate_type='traditional', cate_level=1, book_count=1))
    await db.flush()

    # 书籍 / 卷 / 章节 / 段落
    for book_data in SAMPLE_BOOKS:
        book = content_do.GujiBook(**book_data, has_main_content=1, book_status='published')
        db.add(book)
        await db.flush()
        volume = content_do.GujiVolume(
            book_id=book.book_id, volume_name='卷一', volume_order=1, has_main_content=1, editors='识典古籍整理组'
        )
        db.add(volume)
        await db.flush()
        for order, chapter_name in enumerate(SAMPLE_CHAPTERS[book.book_name]):
            chapter = content_do.GujiChapter(
                book_id=book.book_id,
                volume_id=volume.volume_id,
                chapter_name=chapter_name,
                str_chapter_name=chapter_name,
                chapter_level=1,
                chapter_order=order + 1,
                has_main_content=1,
            )
            db.add(chapter)
            await db.flush()
            for index, (content, translation, annotation) in enumerate(SAMPLE_PARAGRAPHS):
                db.add(
                    content_do.GujiParagraph(
                        book_id=book.book_id,
                        volume_id=volume.volume_id,
                        chapter_id=chapter.chapter_id,
                        chapter_name=chapter_name,
                        para_index=index + 1,
                        content=content,
                        translation=translation,
                        annotation=annotation,
                        content_type='NORMAL',
                    )
                )
        # 音频
        db.add(
            media_do.GujiAudio(
                book_id=book.book_id,
                chapter_id=None,
                audio_title=f'{book.book_name}·朗读',
                listen_type='origin',
                speaker_type='female',
                duration=600,
                uri=f'https://cdn.shidianguji.com/audio/{book.book_id}.mp3',
            )
        )
        # 贡献者
        db.add(
            content_do.GujiContributor(
                book_id=book.book_id,
                user_id=1,
                nick_name='识典古籍整理组',
                contributor_type='contributor',
                contribution_count=120,
            )
        )
    await db.flush()

    # 名句
    for quote, book_name, author, dynasty, cate_name in SAMPLE_QUOTATIONS:
        book = (await db.execute(select_book_by_name(book_name))).scalars().first()
        db.add(
            content_do.GujiQuotation(
                book_id=book.book_id if book else 0,
                book_name=book_name,
                famous_quote=quote,
                author=author,
                dynasty_category=dynasty,
                cate_name=cate_name,
                favorites_num=100,
            )
        )
    await db.flush()

    # 视频 / 课程 / 讲书系列
    course = media_do.GujiVideoCourse(
        course_name='论语精读',
        general_author='识典讲书',
        description='逐章讲解《论语》核心思想。',
        video_num=4,
        updated_to_episode=4,
    )
    db.add(course)
    await db.flush()
    for episode in range(1, 5):
        db.add(
            media_do.GujiVideo(
                collection_id=course.course_id,
                video_name=f'论语精读 第{episode}讲',
                general_author='识典讲书',
                episode=episode,
                uri=f'https://cdn.shidianguji.com/video/{episode}.mp4',
            )
        )
    series = media_do.GujiCourseSeries(
        series_title='论语今读',
        book_name='论语',
        author='识典讲书',
        description='以现代视角重读《论语》。',
        explain_num=4,
    )
    db.add(series)
    await db.flush()
    for order in range(1, 5):
        db.add(
            media_do.GujiCourseExplain(
                series_id=series.series_id,
                explain_title=f'第{order}讲',
                content=f'本讲解读《论语》第{order}章。',
                order_num=order,
            )
        )

    # 首页 Banner 与推荐位
    db.add(
        media_do.GujiHomepageBanner(
            title='识典古籍·免费阅读',
            images=json.dumps({'800': 'https://lf3-static.bytednsdoc.com/obj/eden-cn/banner.webp'}, ensure_ascii=False),
            schema_url='guji://book/1',
            order_num=1,
        )
    )
    for order, book_data in enumerate(SAMPLE_BOOKS):
        db.add(
            media_do.GujiRecommend(
                module_key='recommend',
                module_title='今日推荐',
                biz_type='book',
                biz_id=str(order + 1),
                title=book_data['book_name'],
                sub_title=book_data['authors'],
                schema_url=f'guji://book/{order + 1}',
                order_num=order,
            )
        )
    db.add(media_do.GujiPreferencesTag(tag_name='经部', tag_type='traditional', order_num=1))
    db.add(media_do.GujiPreferencesTag(tag_name='史部', tag_type='traditional', order_num=2))
    db.add(media_do.GujiTeam(team_name='识典古籍整理团队', team_desc='负责古籍数字化整理与校对', member_count=32))

    # 系统通知
    for title, content in [
        ('《论语》新增全本注疏', '《论语》已完成全本注疏整理，可在阅读器开启注疏显示查看。'),
        ('阅读打卡活动上线', '连续打卡 7 天可解锁"笃学"等级权益，记得每天来读一读。'),
        ('听书功能更新', '《道德经》全新朗读音频已上线，可在听书页试听。'),
    ]:
        db.add(user_do.GujiNotice(title=title, content=content, notice_type='system', status='0'))
    await db.flush()


def select_category(name: str):
    """
    构造按分类名查询的语句

    :param name: 分类名
    :return: SQL 语句
    """
    from sqlalchemy import select

    return select(content_do.GujiCategory).where(content_do.GujiCategory.cate_name == name)


def select_book_by_name(name: str):
    """
    构造按书名查询的语句

    :param name: 书名
    :return: SQL 语句
    """
    from sqlalchemy import select

    return select(content_do.GujiBook).where(content_do.GujiBook.book_name == name)


async def main() -> None:
    """
    初始化古籍模块数据表与示例数据

    :return:
    """
    from config.database import DataSourceRegistry

    await DataSourceRegistry.initialize(log_enabled=False)
    async with DataSourceRegistry.connection() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.commit()
    async with DataSourceRegistry.session() as session:
        await _seed(session)
        await session.commit()
    print('识典古籍模块数据表与示例数据初始化完成')


if __name__ == '__main__':
    asyncio.run(main())
