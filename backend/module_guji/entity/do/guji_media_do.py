"""
识典古籍模块 - 媒体域数据库模型

包含听书音频、播客、歌词句、视频、视频课程、讲书系列与讲解、首页 Banner、首页推荐等表。
"""

from sqlalchemy import Column, Integer, String, Text

from common.mixin import AuditTimeMixin
from config.database import Base


class GujiAudio(AuditTimeMixin, Base):
    """
    音频表（听书原文/译文、播客、讲书共用）
    """

    __tablename__ = 'guji_audio'
    __table_args__ = {'comment': '音频表'}

    audio_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='音频ID')
    vid = Column(String(64), nullable=True, comment='视频/播放鉴权ID')
    book_id = Column(Integer, nullable=True, comment='书籍ID')
    volume_id = Column(Integer, nullable=True, comment='卷ID')
    chapter_id = Column(Integer, nullable=True, comment='章节ID')
    str_chapter_name = Column(String(255), nullable=True, comment='章节名')
    series_id = Column(Integer, nullable=True, comment='系列ID')
    audio_title = Column(String(255), nullable=True, comment='音频标题')
    listen_type = Column(String(32), nullable=True, server_default='origin', comment='收听类型（原文/译文/讲书/播客）')
    audio_type = Column(String(32), nullable=True, comment='音频类型')
    speaker = Column(String(64), nullable=True, comment='播音人')
    speaker_type = Column(String(16), nullable=True, comment='音色（男声/女声）')
    duration = Column(Integer, nullable=True, server_default='0', comment='时长（秒）')
    url_list = Column(Text, nullable=True, comment='播放地址JSON')
    uri = Column(String(512), nullable=True, comment='播放URI')
    thumb_url = Column(String(512), nullable=True, comment='封面')
    audio_version = Column(String(32), nullable=True, comment='音频版本')
    podcast_order = Column(Integer, nullable=True, server_default='0', comment='播客集数')
    play_count = Column(Integer, nullable=True, server_default='0', comment='播放次数')
    status = Column(String(16), nullable=True, server_default='published', comment='状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiAudioLyric(AuditTimeMixin, Base):
    """
    音频逐句歌词表
    """

    __tablename__ = 'guji_audio_lyric'
    __table_args__ = {'comment': '音频歌词表'}

    lyric_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='歌词ID')
    audio_id = Column(Integer, nullable=False, comment='音频ID')
    sentence_id = Column(String(64), nullable=True, comment='句子ID')
    audio_index = Column(Integer, nullable=True, server_default='0', comment='句序号')
    total_lyric_part = Column(Integer, nullable=True, server_default='0', comment='总句数')
    content = Column(Text, nullable=True, comment='句内容')
    translation = Column(Text, nullable=True, comment='句译文')
    start_timestamp_ms = Column(Integer, nullable=True, server_default='0', comment='起始毫秒')
    end_timestamp_ms = Column(Integer, nullable=True, server_default='0', comment='结束毫秒')
    paragraph_id = Column(Integer, nullable=True, comment='关联段落ID')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiVideo(AuditTimeMixin, Base):
    """
    视频表
    """

    __tablename__ = 'guji_video'
    __table_args__ = {'comment': '视频表'}

    video_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='视频ID')
    collection_id = Column(Integer, nullable=True, comment='合集ID')
    collection_name = Column(String(255), nullable=True, comment='合集名')
    video_name = Column(String(255), nullable=True, comment='视频名')
    video_type = Column(String(32), nullable=True, comment='视频类型')
    general_author = Column(String(128), nullable=True, comment='主讲')
    cover_url = Column(String(512), nullable=True, comment='封面')
    thumb_url = Column(String(512), nullable=True, comment='缩略图')
    uri = Column(String(512), nullable=True, comment='播放URI')
    url_list = Column(Text, nullable=True, comment='播放地址JSON')
    url_encrypt_type = Column(String(32), nullable=True, comment='加密类型')
    duration = Column(Integer, nullable=True, server_default='0', comment='时长（秒）')
    episode = Column(Integer, nullable=True, server_default='0', comment='集数')
    like_count = Column(Integer, nullable=True, server_default='0', comment='点赞数')
    play_count = Column(Integer, nullable=True, server_default='0', comment='播放数')
    status = Column(String(16), nullable=True, server_default='published', comment='状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiVideoCourse(AuditTimeMixin, Base):
    """
    视频课程/合集表
    """

    __tablename__ = 'guji_video_course'
    __table_args__ = {'comment': '视频课程表'}

    course_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='课程ID')
    collection_id = Column(String(64), nullable=True, comment='外部合集ID')
    course_name = Column(String(255), nullable=True, comment='课程名')
    collection_name = Column(String(255), nullable=True, comment='合集名')
    general_author = Column(String(128), nullable=True, comment='主讲')
    cover_url = Column(String(512), nullable=True, comment='封面')
    description = Column(Text, nullable=True, comment='简介')
    video_num = Column(Integer, nullable=True, server_default='0', comment='视频数量')
    updated_to_episode = Column(Integer, nullable=True, server_default='0', comment='更新至第几集')
    status = Column(String(16), nullable=True, server_default='published', comment='状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiCourseSeries(AuditTimeMixin, Base):
    """
    讲书系列表（course-series）
    """

    __tablename__ = 'guji_course_series'
    __table_args__ = {'comment': '讲书系列表'}

    series_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='系列ID')
    series_title = Column(String(255), nullable=True, comment='系列标题')
    course_name = Column(String(255), nullable=True, comment='课程名')
    book_id = Column(Integer, nullable=True, comment='关联书籍ID')
    book_name = Column(String(255), nullable=True, comment='关联书名')
    author = Column(String(128), nullable=True, comment='讲书人')
    cover_url = Column(String(512), nullable=True, comment='封面')
    description = Column(Text, nullable=True, comment='简介')
    category = Column(String(64), nullable=True, comment='分类')
    explain_num = Column(Integer, nullable=True, server_default='0', comment='讲解数量')
    status = Column(String(16), nullable=True, server_default='published', comment='状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiCourseExplain(AuditTimeMixin, Base):
    """
    讲书讲解表（course-explain）
    """

    __tablename__ = 'guji_course_explain'
    __table_args__ = {'comment': '讲书讲解表'}

    explain_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='讲解ID')
    series_id = Column(Integer, nullable=True, comment='系列ID')
    book_id = Column(Integer, nullable=True, comment='关联书籍ID')
    chapter_id = Column(Integer, nullable=True, comment='关联章节ID')
    paragraph_id = Column(Integer, nullable=True, comment='关联段落ID')
    explain_title = Column(String(255), nullable=True, comment='讲解标题')
    content = Column(Text, nullable=True, comment='讲解内容')
    audio_id = Column(Integer, nullable=True, comment='音频ID')
    order_num = Column(Integer, nullable=True, server_default='0', comment='排序')
    status = Column(String(16), nullable=True, server_default='published', comment='状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiHomepageBanner(AuditTimeMixin, Base):
    """
    首页 Banner 表
    """

    __tablename__ = 'guji_homepage_banner'
    __table_args__ = {'comment': '首页Banner表'}

    banner_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='BannerID')
    title = Column(String(255), nullable=True, comment='标题')
    images = Column(Text, nullable=True, comment='图片JSON（359/500/800）')
    schema_url = Column(String(512), nullable=True, comment='跳转schema')
    start_time = Column(String(32), nullable=True, comment='开始时间')
    expired_time = Column(String(32), nullable=True, comment='过期时间')
    order_num = Column(Integer, nullable=True, server_default='0', comment='排序')
    status = Column(String(1), nullable=True, server_default='0', comment='状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiRecommend(AuditTimeMixin, Base):
    """
    首页推荐位表（板块化配置：推荐书籍/视频/课程/名句/话题）
    """

    __tablename__ = 'guji_recommend'
    __table_args__ = {'comment': '首页推荐表'}

    recommend_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='推荐ID')
    module_key = Column(String(64), nullable=True, comment='板块键')
    module_title = Column(String(128), nullable=True, comment='板块标题')
    biz_type = Column(String(32), nullable=True, comment='业务类型（book/video/course/quotation/topic）')
    biz_id = Column(String(64), nullable=True, comment='业务ID')
    title = Column(String(255), nullable=True, comment='展示标题')
    sub_title = Column(String(255), nullable=True, comment='副标题')
    cover_url = Column(String(512), nullable=True, comment='封面')
    schema_url = Column(String(512), nullable=True, comment='跳转schema')
    order_num = Column(Integer, nullable=True, server_default='0', comment='排序')
    status = Column(String(1), nullable=True, server_default='0', comment='状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiPreferencesTag(AuditTimeMixin, Base):
    """
    冷启动偏好标签表
    """

    __tablename__ = 'guji_preferences_tag'
    __table_args__ = {'comment': '偏好标签表'}

    tag_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='标签ID')
    tag_name = Column(String(64), nullable=True, comment='标签名')
    tag_type = Column(String(32), nullable=True, comment='标签类型')
    cover_url = Column(String(512), nullable=True, comment='封面')
    order_num = Column(Integer, nullable=True, server_default='0', comment='排序')
    status = Column(String(1), nullable=True, server_default='0', comment='状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiPreferencesTagBook(AuditTimeMixin, Base):
    """
    冷启动偏好标签关联书籍表
    """

    __tablename__ = 'guji_preferences_tag_book'
    __table_args__ = {'comment': '偏好标签书籍表'}

    tag_book_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='关联ID')
    tag_id = Column(Integer, nullable=False, comment='标签ID')
    book_id = Column(Integer, nullable=False, comment='书籍ID')
    order_num = Column(Integer, nullable=True, server_default='0', comment='排序')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiTeam(AuditTimeMixin, Base):
    """
    古籍整理团队表
    """

    __tablename__ = 'guji_team'
    __table_args__ = {'comment': '整理团队表'}

    team_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='团队ID')
    team_name = Column(String(128), nullable=True, comment='团队名')
    team_desc = Column(Text, nullable=True, comment='团队介绍')
    logo_url = Column(String(512), nullable=True, comment='团队LOGO')
    member_count = Column(Integer, nullable=True, server_default='0', comment='成员数')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')
