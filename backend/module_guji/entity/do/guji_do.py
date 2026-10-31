from sqlalchemy import BigInteger, Column, Integer, String, Text

from common.mixin import AuditTimeMixin
from common.types import DbUtcDateTime
from config.database import Base


class GujiBook(AuditTimeMixin, Base):
    """古籍书目表"""

    __tablename__ = 'guji_book'
    __table_args__ = {'comment': '古籍书目表'}

    book_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='书目ID')
    book_name = Column(String(100), nullable=False, comment='书名')
    author = Column(String(50), nullable=True, server_default='', comment='作者')
    dynasty = Column(String(20), nullable=True, server_default='', comment='朝代')
    category = Column(String(20), nullable=True, server_default='', comment='分类（经/史/子/集/蒙学）')
    intro = Column(String(1000), nullable=True, server_default='', comment='内容简介')
    cover = Column(String(255), nullable=True, server_default='', comment='封面图URL')
    chapter_count = Column(Integer, nullable=True, server_default='0', comment='章节数')
    status = Column(String(1), nullable=True, server_default='0', comment='状态（0上架 1下架）')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志（0存在 2删除）')
    create_by = Column(String(64), nullable=True, server_default='', comment='创建者')
    create_time = Column(DbUtcDateTime(), nullable=True, comment='创建时间')
    update_by = Column(String(64), nullable=True, server_default='', comment='更新者')
    update_time = Column(DbUtcDateTime(), nullable=True, comment='更新时间')


class GujiChapter(Base):
    """古籍章节表"""

    __tablename__ = 'guji_chapter'
    __table_args__ = {'comment': '古籍章节表'}

    chapter_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='章节ID')
    book_id = Column(BigInteger, nullable=False, comment='所属书目ID')
    chapter_no = Column(Integer, nullable=True, server_default='0', comment='章节序号')
    chapter_name = Column(String(100), nullable=True, server_default='', comment='章节标题')
    paragraph_count = Column(Integer, nullable=True, server_default='0', comment='段落数')
    create_time = Column(DbUtcDateTime(), nullable=True, comment='创建时间')
    update_time = Column(DbUtcDateTime(), nullable=True, comment='更新时间')


class GujiParagraph(Base):
    """古籍段落表"""

    __tablename__ = 'guji_paragraph'
    __table_args__ = {'comment': '古籍段落表'}

    paragraph_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='段落ID')
    chapter_id = Column(BigInteger, nullable=False, comment='所属章节ID')
    book_id = Column(BigInteger, nullable=False, comment='所属书目ID')
    para_seq = Column(Integer, nullable=True, server_default='0', comment='段落序号')
    para_text = Column(Text, nullable=True, comment='段落文本')


class GujiBookshelf(AuditTimeMixin, Base):
    """古籍书架表"""

    __tablename__ = 'guji_bookshelf'
    __table_args__ = {'comment': '古籍书架表'}

    shelf_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='书架ID')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    book_id = Column(BigInteger, nullable=False, comment='书目ID')
    last_chapter_id = Column(BigInteger, nullable=True, server_default='0', comment='最后阅读章节ID')
    last_paragraph_id = Column(BigInteger, nullable=True, server_default='0', comment='最后阅读段落ID')
    create_time = Column(DbUtcDateTime(), nullable=True, comment='收藏时间')
    update_time = Column(DbUtcDateTime(), nullable=True, comment='更新时间')


class GujiReadHistory(Base):
    """古籍阅读历史表"""

    __tablename__ = 'guji_read_history'
    __table_args__ = {'comment': '古籍阅读历史表'}

    history_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='历史ID')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    book_id = Column(BigInteger, nullable=False, comment='书目ID')
    chapter_id = Column(BigInteger, nullable=True, server_default='0', comment='章节ID')
    paragraph_id = Column(BigInteger, nullable=True, server_default='0', comment='段落ID')
    read_time = Column(DbUtcDateTime(), nullable=True, comment='阅读时间')


class GujiAudio(Base):
    """古籍听书音频表"""

    __tablename__ = 'guji_audio'
    __table_args__ = {'comment': '古籍听书音频表'}

    audio_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='音频ID')
    book_id = Column(BigInteger, nullable=False, comment='书目ID')
    chapter_id = Column(BigInteger, nullable=True, server_default='0', comment='章节ID（0为全书音频）')
    audio_name = Column(String(100), nullable=True, server_default='', comment='音频名称')
    audio_url = Column(String(255), nullable=True, server_default='', comment='音频地址')
    duration_sec = Column(Integer, nullable=True, server_default='0', comment='时长（秒）')
    create_time = Column(DbUtcDateTime(), nullable=True, comment='创建时间')
