"""
识典古籍模块 - 用户域数据库模型

包含书架、阅读历史、书签、笔记、收藏、话题书单、用户偏好、打卡、等级、通知、AI会话等表。
书架采用 shelf_biz_type 让书籍/视频/课程共用同一张表，与原 App 的 V4 接口设计一致。
"""

from sqlalchemy import Column, Integer, String, Text, UniqueConstraint

from common.mixin import AuditTimeMixin
from config.database import Base


class GujiBookshelf(AuditTimeMixin, Base):
    """
    书架表（书籍/视频/课程共用，由 shelf_biz_type 区分）
    """

    __tablename__ = 'guji_bookshelf'
    __table_args__ = (
        UniqueConstraint('user_id', 'biz_id', 'shelf_biz_type', name='uk_guji_bookshelf'),
        {'comment': '书架表'},
    )

    shelf_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='书架ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    biz_id = Column(String(64), nullable=False, comment='业务ID（bookId/videoId/courseId）')
    shelf_biz_type = Column(String(32), nullable=True, server_default='book', comment='业务类型')
    group_id = Column(String(64), nullable=True, comment='分组ID')
    group_name = Column(String(128), nullable=True, comment='分组名')
    progress = Column(String(64), nullable=True, comment='阅读进度')
    progress_detail = Column(Text, nullable=True, comment='进度详情JSON')
    last_read_time = Column(String(32), nullable=True, comment='最后阅读时间')
    last_open_time = Column(String(32), nullable=True, comment='最后打开时间')
    operation_time_ms = Column(String(32), nullable=True, comment='客户端操作时间戳')
    is_finished = Column(Integer, nullable=True, server_default='0', comment='是否已读完')
    offline_task = Column(Integer, nullable=True, server_default='0', comment='离线缓存任务')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiReadHistory(AuditTimeMixin, Base):
    """
    阅读历史表
    """

    __tablename__ = 'guji_read_history'
    __table_args__ = (
        UniqueConstraint('user_id', 'biz_id', 'shelf_biz_type', name='uk_guji_read_history'),
        {'comment': '阅读历史表'},
    )

    history_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='历史ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    biz_id = Column(String(64), nullable=False, comment='业务ID')
    shelf_biz_type = Column(String(32), nullable=True, server_default='book', comment='业务类型')
    book_id = Column(Integer, nullable=True, comment='书籍ID')
    chapter_id = Column(Integer, nullable=True, comment='章节ID')
    chapter_name = Column(String(255), nullable=True, comment='章节名')
    progress = Column(String(64), nullable=True, comment='阅读进度')
    progress_detail = Column(Text, nullable=True, comment='进度详情JSON')
    last_content = Column(Text, nullable=True, comment='最后阅读内容')
    version = Column(String(32), nullable=True, comment='版本')
    last_read_time = Column(String(32), nullable=True, comment='最后阅读时间')
    last_open_time = Column(String(32), nullable=True, comment='最后打开时间')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiBookmark(AuditTimeMixin, Base):
    """
    书签表
    """

    __tablename__ = 'guji_bookmark'
    __table_args__ = {'comment': '书签表'}

    bookmark_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='书签ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    book_id = Column(Integer, nullable=False, comment='书籍ID')
    chapter_id = Column(Integer, nullable=True, comment='章节ID')
    chapter_name = Column(String(255), nullable=True, comment='章节名')
    chapter_start_index = Column(Integer, nullable=True, server_default='0', comment='起始下标')
    chapter_end_index = Column(Integer, nullable=True, server_default='0', comment='结束下标')
    marked_text = Column(Text, nullable=True, comment='划线文本')
    marked_text_position = Column(Text, nullable=True, comment='划线位置JSON')
    bookmark_style = Column(String(32), nullable=True, comment='书签样式')
    color_style = Column(String(32), nullable=True, comment='颜色样式')
    volume_version = Column(String(32), nullable=True, comment='卷版本')
    context = Column(Text, nullable=True, comment='上下文')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiReview(AuditTimeMixin, Base):
    """
    用户笔记/批注表
    """

    __tablename__ = 'guji_review'
    __table_args__ = {'comment': '用户笔记表'}

    review_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='笔记ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    book_id = Column(Integer, nullable=False, comment='书籍ID')
    chapter_id = Column(Integer, nullable=True, comment='章节ID')
    chapter_name = Column(String(255), nullable=True, comment='章节名')
    chapter_start_index = Column(Integer, nullable=True, server_default='0', comment='起始下标')
    chapter_end_index = Column(Integer, nullable=True, server_default='0', comment='结束下标')
    marked_text = Column(Text, nullable=True, comment='划线文本')
    marked_text_position = Column(Text, nullable=True, comment='划线位置JSON')
    review_type = Column(String(32), nullable=True, server_default='note', comment='笔记类型')
    content = Column(Text, nullable=True, comment='笔记内容')
    volume_version = Column(String(32), nullable=True, comment='卷版本')
    volume_status = Column(String(32), nullable=True, comment='卷状态')
    context = Column(Text, nullable=True, comment='上下文')
    status = Column(String(16), nullable=True, server_default='normal', comment='状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiFavorite(AuditTimeMixin, Base):
    """
    通用收藏表（名句、书籍等共用，由 biz_type + biz_id 定位）
    """

    __tablename__ = 'guji_favorite'
    __table_args__ = (
        UniqueConstraint('user_id', 'biz_type', 'biz_id', name='uk_guji_favorite'),
        {'comment': '通用收藏表'},
    )

    favorite_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='收藏ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    biz_type = Column(String(32), nullable=True, server_default='quotation', comment='业务类型')
    biz_id = Column(String(64), nullable=False, comment='业务ID')
    title = Column(String(255), nullable=True, comment='标题快照')
    cover_url = Column(String(512), nullable=True, comment='封面快照')
    extra = Column(Text, nullable=True, comment='扩展信息JSON')
    favorite_time = Column(String(32), nullable=True, comment='收藏时间')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiTopic(AuditTimeMixin, Base):
    """
    话题/书单表
    """

    __tablename__ = 'guji_topic'
    __table_args__ = {'comment': '话题书单表'}

    topic_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='话题ID')
    user_id = Column(Integer, nullable=True, comment='创建人ID')
    title = Column(String(255), nullable=True, comment='标题')
    description = Column(Text, nullable=True, comment='描述')
    cover_url = Column(String(512), nullable=True, comment='封面')
    library_id = Column(Integer, nullable=True, comment='话题库ID')
    is_private = Column(Integer, nullable=True, server_default='0', comment='是否私有')
    topic_show_status = Column(String(32), nullable=True, server_default='published', comment='展示状态')
    follow_count = Column(Integer, nullable=True, server_default='0', comment='关注数')
    view_count = Column(Integer, nullable=True, server_default='0', comment='浏览数')
    book_num = Column(Integer, nullable=True, server_default='0', comment='书籍数量')
    order_num = Column(Integer, nullable=True, server_default='0', comment='排序')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiTopicBook(AuditTimeMixin, Base):
    """
    话题书单关联书籍表
    """

    __tablename__ = 'guji_topic_book'
    __table_args__ = (
        UniqueConstraint('topic_id', 'book_id', name='uk_guji_topic_book'),
        {'comment': '话题书籍关联表'},
    )

    topic_book_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='关联ID')
    topic_id = Column(Integer, nullable=False, comment='话题ID')
    book_id = Column(Integer, nullable=False, comment='书籍ID')
    book_name = Column(String(255), nullable=True, comment='书名快照')
    cover_url = Column(String(512), nullable=True, comment='封面快照')
    recommendation = Column(Text, nullable=True, comment='推荐语')
    order_num = Column(Integer, nullable=True, server_default='0', comment='排序')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiTopicFollow(AuditTimeMixin, Base):
    """
    话题关注表
    """

    __tablename__ = 'guji_topic_follow'
    __table_args__ = (
        UniqueConstraint('user_id', 'topic_id', name='uk_guji_topic_follow'),
        {'comment': '话题关注表'},
    )

    follow_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='关注ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    topic_id = Column(Integer, nullable=False, comment='话题ID')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiUserPreference(AuditTimeMixin, Base):
    """
    用户阅读偏好设置表（字号、字体、主题、简繁、推送等）
    """

    __tablename__ = 'guji_user_preference'
    __table_args__ = {'comment': '用户阅读偏好表'}

    preference_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='偏好ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    preference_key = Column(String(64), nullable=False, comment='偏好键')
    preference_value = Column(Text, nullable=True, comment='偏好值JSON')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiUserClock(AuditTimeMixin, Base):
    """
    阅读打卡记录表
    """

    __tablename__ = 'guji_user_clock'
    __table_args__ = {'comment': '阅读打卡表'}

    clock_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='打卡ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    book_id = Column(Integer, nullable=True, comment='书籍ID')
    clock_date = Column(String(16), nullable=True, comment='打卡日期yyyy-MM-dd')
    reading_time = Column(Integer, nullable=True, server_default='0', comment='当日阅读时长（秒）')
    client_timestamp_ms = Column(String(32), nullable=True, comment='客户端时间戳')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiUserLevel(AuditTimeMixin, Base):
    """
    用户等级与贡献表
    """

    __tablename__ = 'guji_user_level'
    __table_args__ = (
        UniqueConstraint('user_id', name='uk_guji_user_level'),
        {'comment': '用户等级表'},
    )

    level_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='等级ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    level = Column(Integer, nullable=True, server_default='1', comment='等级')
    clock_days = Column(Integer, nullable=True, server_default='0', comment='累计打卡天数')
    continue_days = Column(Integer, nullable=True, server_default='0', comment='连续打卡天数')
    total_reading_time = Column(Integer, nullable=True, server_default='0', comment='累计阅读时长（秒）')
    contribution_str = Column(String(255), nullable=True, comment='贡献描述')
    contribution_count = Column(Integer, nullable=True, server_default='0', comment='贡献次数')
    expired_time = Column(String(32), nullable=True, comment='权益过期时间')


class GujiLevelGiftOrder(AuditTimeMixin, Base):
    """
    等级权益兑换订单表
    """

    __tablename__ = 'guji_level_gift_order'
    __table_args__ = {'comment': '等级权益订单表'}

    order_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='订单ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    parent_order_id = Column(String(64), nullable=True, comment='父订单号')
    sku_list = Column(Text, nullable=True, comment='商品列表JSON')
    address = Column(Text, nullable=True, comment='收货地址JSON')
    mark_name = Column(String(128), nullable=True, comment='备注名')
    order_status = Column(String(32), nullable=True, server_default='created', comment='订单状态')
    way_bill_no = Column(String(64), nullable=True, comment='运单号')
    logistics_company_name = Column(String(128), nullable=True, comment='物流公司')
    token = Column(String(128), nullable=True, comment='校验token')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiNotice(AuditTimeMixin, Base):
    """
    古籍业务通知表
    """

    __tablename__ = 'guji_notice'
    __table_args__ = {'comment': '古籍通知表'}

    notice_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='通知ID')
    title = Column(String(255), nullable=True, comment='标题')
    content = Column(Text, nullable=True, comment='内容')
    notice_type = Column(String(32), nullable=True, server_default='system', comment='通知类型')
    publish_time = Column(String(32), nullable=True, comment='发布时间')
    status = Column(String(1), nullable=True, server_default='0', comment='状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiNoticeRead(AuditTimeMixin, Base):
    """
    通知已读记录表
    """

    __tablename__ = 'guji_notice_read'
    __table_args__ = (
        UniqueConstraint('user_id', 'notice_id', name='uk_guji_notice_read'),
        {'comment': '通知已读表'},
    )

    read_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='已读ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    notice_id = Column(Integer, nullable=False, comment='通知ID')
    read_time = Column(String(32), nullable=True, comment='已读时间')


class GujiAssistantChat(AuditTimeMixin, Base):
    """
    古籍智能助手会话/消息表
    """

    __tablename__ = 'guji_assistant_chat'
    __table_args__ = {'comment': 'AI助手会话表'}

    chat_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='会话ID')
    user_id = Column(Integer, nullable=True, comment='用户ID')
    session_id = Column(String(64), nullable=True, comment='会话标识')
    book_id = Column(Integer, nullable=True, comment='关联书籍ID')
    chapter_id = Column(Integer, nullable=True, comment='关联章节ID')
    role = Column(String(16), nullable=True, server_default='user', comment='角色（user/assistant）')
    question = Column(Text, nullable=True, comment='提问')
    answer = Column(Text, nullable=True, comment='回答')
    context = Column(Text, nullable=True, comment='补充上下文JSON')
    feedback = Column(String(32), nullable=True, comment='反馈（up/down）')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiUserAddress(AuditTimeMixin, Base):
    """
    用户收货地址表
    """

    __tablename__ = 'guji_user_address'
    __table_args__ = {'comment': '用户收货地址表'}

    address_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='地址ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    receiver_name = Column(String(64), nullable=True, comment='收货人')
    phone = Column(String(32), nullable=True, comment='手机号')
    province = Column(String(64), nullable=True, comment='省')
    city = Column(String(64), nullable=True, comment='市')
    district = Column(String(64), nullable=True, comment='区')
    detail = Column(String(255), nullable=True, comment='详细地址')
    is_default = Column(Integer, nullable=True, server_default='0', comment='是否默认')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiUserTag(AuditTimeMixin, Base):
    """
    用户偏好标签表（冷启动兴趣标签）
    """

    __tablename__ = 'guji_user_tag'
    __table_args__ = {'comment': '用户偏好标签表'}

    tag_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='标签ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    tag_name = Column(String(64), nullable=True, comment='标签名')
    tag_book_ids = Column(Text, nullable=True, comment='标签关联书籍ID')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')
