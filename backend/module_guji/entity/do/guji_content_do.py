"""
识典古籍模块 - 内容域数据库模型

包含书籍、卷、章节、段落、分类、贡献者、名句、实体、字典字形等表。
字段命名与 App 端接口字段保持一致（驼峰 -> 下划线，对外由 CamelCaseUtil 转换）。
"""

from sqlalchemy import Column, Integer, String, Text, UniqueConstraint

from common.mixin import AuditTimeMixin
from config.database import Base


class GujiBook(AuditTimeMixin, Base):
    """
    古籍书籍表
    """

    __tablename__ = 'guji_book'
    __table_args__ = {'comment': '古籍书籍表'}

    book_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='书籍ID')
    book_name = Column(String(255), nullable=False, server_default='', comment='书名')
    add_names = Column(Text, nullable=True, comment='增补名/别名，逗号分隔')
    authors = Column(Text, nullable=True, comment='作者，逗号分隔')
    dynasty_category_id = Column(Integer, nullable=True, comment='朝代分类ID')
    dynasty_category_name = Column(String(64), nullable=True, comment='朝代分类名')
    dynasty_name = Column(String(64), nullable=True, comment='朝代名')
    dynasty_cate_id = Column(Integer, nullable=True, comment='朝代展示分类ID')
    traditional_category = Column(String(32), nullable=True, comment='传统四部分类（经史子集）')
    modern_category = Column(String(64), nullable=True, comment='现代分类')
    cover_url = Column(String(512), nullable=True, comment='封面地址')
    cover_uri = Column(String(512), nullable=True, comment='封面URI')
    beautiful_cover = Column(String(512), nullable=True, comment='精美封面地址')
    image_source = Column(String(128), nullable=True, comment='图像来源')
    image_source_url = Column(String(512), nullable=True, comment='图像来源地址')
    publication_stmt = Column(Text, nullable=True, comment='出版说明')
    abstract = Column(Text, nullable=True, comment='内容简介')
    introduction = Column(Text, nullable=True, comment='导读')
    short_introduction = Column(Text, nullable=True, comment='短导读')
    catalog = Column(Text, nullable=True, comment='目录说明')
    edition = Column(String(255), nullable=True, comment='版本/底本')
    license = Column(String(255), nullable=True, comment='授权协议')
    protocol_type = Column(String(32), nullable=True, comment='协议类型')
    protocol_url = Column(String(512), nullable=True, comment='协议地址')
    library = Column(String(255), nullable=True, comment='藏书机构')
    team_id = Column(Integer, nullable=True, comment='整理团队ID')
    responsible_type_str = Column(String(128), nullable=True, comment='责任者类型')
    distributor = Column(String(255), nullable=True, comment='发行方')
    pers_name = Column(String(255), nullable=True, comment='责任者人名')
    importance_level = Column(Integer, nullable=True, server_default='0', comment='重要度')
    popularity = Column(Integer, nullable=True, server_default='0', comment='热度')
    book_status = Column(String(16), nullable=True, server_default='published', comment='书籍状态')
    has_main_content = Column(Integer, nullable=True, server_default='0', comment='是否有正文')
    is_listening_supported = Column(Integer, nullable=True, server_default='0', comment='是否支持听书')
    is_podcast_supported = Column(Integer, nullable=True, server_default='0', comment='是否支持讲书')
    total_page = Column(Integer, nullable=True, server_default='0', comment='总页数')
    preview_pages = Column(Integer, nullable=True, server_default='0', comment='试读页数')
    paragraph_number = Column(Integer, nullable=True, server_default='0', comment='段落数')
    paragraph_size = Column(Integer, nullable=True, server_default='0', comment='段落平均字数')
    version = Column(Integer, nullable=True, server_default='1', comment='正文版本')
    meta_version = Column(Integer, nullable=True, server_default='1', comment='元数据版本')
    pin_yin_version = Column(Integer, nullable=True, server_default='1', comment='拼音版本')
    audio_version = Column(Integer, nullable=True, server_default='1', comment='音频版本')
    four_char_recommendation = Column(String(32), nullable=True, comment='四字推荐语')
    related_video = Column(Text, nullable=True, comment='关联视频JSON')
    quotation = Column(Text, nullable=True, comment='名句JSON')
    book_extra = Column(Text, nullable=True, comment='扩展信息JSON')
    last_mod = Column(String(32), nullable=True, comment='最后修改时间（原始值）')
    status = Column(String(1), nullable=True, server_default='0', comment='状态（0正常 1停用）')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志（0存在 1删除）')
    create_by = Column(String(64), nullable=True, server_default='', comment='创建者')
    update_by = Column(String(64), nullable=True, server_default='', comment='更新者')
    remark = Column(String(500), nullable=True, comment='备注')


class GujiVolume(AuditTimeMixin, Base):
    """
    古籍卷表
    """

    __tablename__ = 'guji_volume'
    __table_args__ = {'comment': '古籍卷表'}

    volume_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='卷ID')
    book_id = Column(Integer, nullable=False, comment='书籍ID')
    volume_name = Column(String(255), nullable=True, comment='卷名')
    volume_order = Column(Integer, nullable=True, server_default='0', comment='卷序号')
    volume_version = Column(Integer, nullable=True, server_default='1', comment='卷版本')
    volume_pin_yin_version = Column(Integer, nullable=True, server_default='1', comment='卷拼音版本')
    has_main_content = Column(Integer, nullable=True, server_default='0', comment='是否有正文')
    bit_status = Column(Integer, nullable=True, server_default='0', comment='位状态')
    editors = Column(String(500), nullable=True, comment='整理者')
    correctors = Column(String(500), nullable=True, comment='校对者')
    edition_dynasty_name = Column(String(64), nullable=True, comment='版本所属朝代')
    translate_status = Column(String(16), nullable=True, comment='译文状态')
    en_translate_status = Column(String(16), nullable=True, comment='英文译文状态')
    paragraph_count = Column(Integer, nullable=True, server_default='0', comment='段落数量')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiChapter(AuditTimeMixin, Base):
    """
    古籍章节/目录表
    """

    __tablename__ = 'guji_chapter'
    __table_args__ = {'comment': '古籍章节表'}

    chapter_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='章节ID')
    book_id = Column(Integer, nullable=False, comment='书籍ID')
    volume_id = Column(Integer, nullable=True, comment='卷ID')
    parent_chapter_id = Column(Integer, nullable=True, comment='父章节ID')
    chapter_name = Column(String(255), nullable=True, comment='章节名')
    str_chapter_name = Column(String(255), nullable=True, comment='字符串化章节名')
    chapter_level = Column(Integer, nullable=True, server_default='1', comment='章节层级')
    chapter_order = Column(Integer, nullable=True, server_default='0', comment='章节排序')
    start_page_num = Column(Integer, nullable=True, server_default='0', comment='起始页码')
    end_page_num_without_subchapter = Column(Integer, nullable=True, server_default='0', comment='不含子章节结束页码')
    paragraph_count = Column(Integer, nullable=True, server_default='0', comment='段落数')
    has_main_content = Column(Integer, nullable=True, server_default='0', comment='是否有正文')
    volume_version = Column(Integer, nullable=True, server_default='1', comment='卷版本')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiParagraph(AuditTimeMixin, Base):
    """
    古籍段落表（一段同时承载原文/注疏/译文/底本原字，由 content_type 区分）
    """

    __tablename__ = 'guji_paragraph'
    __table_args__ = {'comment': '古籍段落表'}

    paragraph_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='段落ID')
    book_id = Column(Integer, nullable=False, comment='书籍ID')
    volume_id = Column(Integer, nullable=True, comment='卷ID')
    chapter_id = Column(Integer, nullable=False, comment='章节ID')
    chapter_name = Column(String(255), nullable=True, comment='章节名')
    para_index = Column(Integer, nullable=True, server_default='0', comment='段落在章节内序号')
    page_num = Column(Integer, nullable=True, server_default='0', comment='页码')
    content_type = Column(
        String(32), nullable=True, server_default='NORMAL', comment='段落类型（NORMAL/TITLE/TABLE/PIC/译文/注疏/校勘）'
    )
    para_source_type = Column(String(32), nullable=True, server_default='origin', comment='来源类型')
    content = Column(Text, nullable=True, comment='正文原文')
    translation = Column(Text, nullable=True, comment='译文')
    annotation = Column(Text, nullable=True, comment='注疏')
    collate = Column(Text, nullable=True, comment='校勘/底本原字')
    pinyin = Column(Text, nullable=True, comment='拼音')
    raw_json = Column(Text, nullable=True, comment='富文本节点树JSON')
    margin_note_id = Column(Integer, nullable=True, comment='关联官方页边注ID')
    book_version = Column(Integer, nullable=True, server_default='1', comment='书籍版本')
    volume_version = Column(Integer, nullable=True, server_default='1', comment='卷版本')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiCategory(AuditTimeMixin, Base):
    """
    古籍分类表（经史子集四部）
    """

    __tablename__ = 'guji_category'
    __table_args__ = {'comment': '古籍分类表'}

    cate_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='分类ID')
    parent_id = Column(Integer, nullable=True, server_default='0', comment='父分类ID')
    cate_name = Column(String(64), nullable=True, comment='分类名')
    cate_type = Column(String(32), nullable=True, server_default='traditional', comment='分类体系')
    cate_level = Column(Integer, nullable=True, server_default='1', comment='层级')
    order_num = Column(Integer, nullable=True, server_default='0', comment='排序')
    book_count = Column(Integer, nullable=True, server_default='0', comment='书籍数量')
    cover_url = Column(String(512), nullable=True, comment='封面')
    description = Column(Text, nullable=True, comment='分类说明')
    status = Column(String(1), nullable=True, server_default='0', comment='状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiContributor(AuditTimeMixin, Base):
    """
    古籍整理者/勘误者表
    """

    __tablename__ = 'guji_contributor'
    __table_args__ = (
        UniqueConstraint('book_id', 'user_id', 'contributor_type', name='uk_guji_contributor'),
        {'comment': '古籍贡献者表'},
    )

    contributor_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='贡献者ID')
    book_id = Column(Integer, nullable=False, comment='书籍ID')
    user_id = Column(Integer, nullable=True, comment='用户ID')
    nick_name = Column(String(64), nullable=True, comment='昵称')
    avatar_url = Column(String(512), nullable=True, comment='头像')
    contributor_type = Column(String(16), nullable=True, server_default='contributor', comment='类型（contributor勘误/corrector校对）')
    contribution_count = Column(Integer, nullable=True, server_default='0', comment='贡献数量')
    order_num = Column(Integer, nullable=True, server_default='0', comment='排序')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiQuotation(AuditTimeMixin, Base):
    """
    古籍名句表
    """

    __tablename__ = 'guji_quotation'
    __table_args__ = {'comment': '古籍名句表'}

    quotation_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='名句ID')
    book_id = Column(Integer, nullable=False, comment='书籍ID')
    book_name = Column(String(255), nullable=True, comment='书名')
    book_version = Column(Integer, nullable=True, server_default='1', comment='书籍版本')
    chapter_id = Column(Integer, nullable=True, comment='章节ID')
    chapter_name = Column(String(255), nullable=True, comment='章节名')
    paragraph_id = Column(Integer, nullable=True, comment='段落ID')
    famous_quote = Column(Text, nullable=True, comment='名句正文')
    translation = Column(Text, nullable=True, comment='名句译文')
    cate_id = Column(Integer, nullable=True, comment='名句分类ID')
    cate_name = Column(String(64), nullable=True, comment='名句分类名')
    author = Column(String(128), nullable=True, comment='作者')
    dynasty_category = Column(String(64), nullable=True, comment='朝代')
    genre = Column(String(64), nullable=True, comment='体裁')
    favorites_num = Column(Integer, nullable=True, server_default='0', comment='收藏数')
    status = Column(String(16), nullable=True, server_default='published', comment='展示状态')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiQuotationCategory(AuditTimeMixin, Base):
    """
    名句分类表
    """

    __tablename__ = 'guji_quotation_category'
    __table_args__ = {'comment': '名句分类表'}

    cate_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='分类ID')
    parent_id = Column(Integer, nullable=True, server_default='0', comment='父分类ID')
    cate_name = Column(String(64), nullable=True, comment='分类名')
    tag = Column(String(64), nullable=True, comment='标签')
    order_num = Column(Integer, nullable=True, server_default='0', comment='排序')
    quotation_count = Column(Integer, nullable=True, server_default='0', comment='名句数量')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiEntity(AuditTimeMixin, Base):
    """
    古籍实体表（人名/地名/官职/典故等）
    """

    __tablename__ = 'guji_entity'
    __table_args__ = {'comment': '古籍实体表'}

    entity_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='实体ID')
    normal_name = Column(String(128), nullable=True, comment='标准名')
    entity_type = Column(String(32), nullable=True, comment='实体类型')
    desc = Column(Text, nullable=True, comment='简介')
    wiki_doc = Column(Text, nullable=True, comment='百科文档JSON')
    baike_doc = Column(Text, nullable=True, comment='抖音百科JSON')
    dynasty = Column(String(64), nullable=True, comment='朝代')
    location_name = Column(String(128), nullable=True, comment='地名')
    longitude = Column(String(32), nullable=True, comment='经度')
    latitude = Column(String(32), nullable=True, comment='纬度')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiEntityRef(AuditTimeMixin, Base):
    """
    实体引用表（实体与段落的关联）
    """

    __tablename__ = 'guji_entity_ref'
    __table_args__ = {'comment': '实体引用表'}

    ref_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='引用ID')
    entity_id = Column(Integer, nullable=False, comment='实体ID')
    entity_name = Column(String(128), nullable=True, comment='实体名')
    book_id = Column(Integer, nullable=True, comment='书籍ID')
    chapter_id = Column(Integer, nullable=True, comment='章节ID')
    paragraph_id = Column(Integer, nullable=True, comment='段落ID')
    chapter_start_index = Column(Integer, nullable=True, server_default='0', comment='起始下标')
    chapter_end_index = Column(Integer, nullable=True, server_default='0', comment='结束下标')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiDictChar(AuditTimeMixin, Base):
    """
    字典字形表（汉字详情、说文/康熙/汉语大词典释义）
    """

    __tablename__ = 'guji_dict_char'
    __table_args__ = (
        UniqueConstraint('char', name='uk_guji_dict_char'),
        {'comment': '字典字形表'},
    )

    char_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='字形ID')
    char = Column(String(8), nullable=False, comment='汉字')
    pinyin = Column(String(128), nullable=True, comment='拼音')
    rad = Column(String(8), nullable=True, comment='部首')
    polyphone = Column(String(128), nullable=True, comment='多音字')
    explain = Column(Text, nullable=True, comment='释义')
    hanyu_doc = Column(Text, nullable=True, comment='汉语大词典JSON')
    kangxi_docs = Column(Text, nullable=True, comment='康熙字典JSON')
    shuowenjiezi_doc = Column(Text, nullable=True, comment='说文解字JSON')
    char_pic_url = Column(String(512), nullable=True, comment='字形图')
    stroke_count = Column(Integer, nullable=True, comment='笔画数')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiMarginNote(AuditTimeMixin, Base):
    """
    官方页边注表
    """

    __tablename__ = 'guji_margin_note'
    __table_args__ = {'comment': '官方页边注表'}

    margin_note_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='页边注ID')
    book_id = Column(Integer, nullable=False, comment='书籍ID')
    chapter_id = Column(Integer, nullable=True, comment='章节ID')
    paragraph_id = Column(Integer, nullable=True, comment='段落ID')
    content = Column(Text, nullable=True, comment='页边注内容')
    resp_person_name = Column(String(64), nullable=True, comment='回复人')
    resp_time = Column(String(32), nullable=True, comment='回复时间')
    del_flag = Column(String(1), nullable=True, server_default='0', comment='删除标志')


class GujiFeedback(AuditTimeMixin, Base):
    """
    内容勘误反馈表
    """

    __tablename__ = 'guji_feedback'
    __table_args__ = {'comment': '内容勘误反馈表'}

    feedback_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment='反馈ID')
    user_id = Column(Integer, nullable=True, comment='用户ID')
    book_id = Column(Integer, nullable=True, comment='书籍ID')
    issue = Column(String(128), nullable=True, comment='问题摘要')
    quote = Column(Text, nullable=True, comment='引用原文')
    email = Column(String(128), nullable=True, comment='联系邮箱')
    issue_type = Column(String(32), nullable=True, comment='问题类型')
    description = Column(Text, nullable=True, comment='问题描述')
    translate_issue = Column(Text, nullable=True, comment='译文问题')
    issue_ori = Column(Text, nullable=True, comment='原文问题')
    cus_description = Column(Text, nullable=True, comment='补充说明')
    status = Column(String(16), nullable=True, server_default='pending', comment='处理状态')
