from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from common.types import ApiUtcDateTime


class GujiBookModel(BaseModel):
    """古籍书目模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    book_id: int | None = Field(default=None, description='书目ID')
    book_name: str | None = Field(default=None, description='书名')
    author: str | None = Field(default=None, description='作者')
    dynasty: str | None = Field(default=None, description='朝代')
    category: str | None = Field(default=None, description='分类（经/史/子/集/蒙学）')
    intro: str | None = Field(default=None, description='内容简介')
    cover: str | None = Field(default=None, description='封面图URL')
    chapter_count: int | None = Field(default=None, description='章节数')


class GujiBookPageQueryModel(GujiBookModel):
    """古籍书目分页查询模型"""

    book_name: str | None = Field(default=None, description='书名（模糊查询）')
    category: str | None = Field(default=None, description='分类（精确匹配）')
    dynasty: str | None = Field(default=None, description='朝代（精确匹配）')
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class GujiChapterModel(BaseModel):
    """古籍章节模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    chapter_id: int | None = Field(default=None, description='章节ID')
    book_id: int | None = Field(default=None, description='所属书目ID')
    chapter_no: int | None = Field(default=None, description='章节序号')
    chapter_name: str | None = Field(default=None, description='章节标题')
    paragraph_count: int | None = Field(default=None, description='段落数')


class GujiParagraphPageQueryModel(BaseModel):
    """古籍段落分页查询模型"""

    model_config = ConfigDict(alias_generator=to_camel)

    chapter_id: int | None = Field(default=None, description='章节ID')
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=20, description='每页记录数')


class GujiParagraphModel(BaseModel):
    """古籍段落模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    paragraph_id: int | None = Field(default=None, description='段落ID')
    chapter_id: int | None = Field(default=None, description='所属章节ID')
    para_seq: int | None = Field(default=None, description='段落序号')
    para_text: str | None = Field(default=None, description='段落文本')


class GujiBookshelfAddModel(BaseModel):
    """加入书架模型"""

    model_config = ConfigDict(alias_generator=to_camel)

    book_id: int = Field(description='书目ID')


class GujiReadHistoryModel(BaseModel):
    """阅读进度上报模型"""

    model_config = ConfigDict(alias_generator=to_camel)

    book_id: int = Field(description='书目ID')
    chapter_id: int = Field(default=0, description='章节ID')
    paragraph_id: int = Field(default=0, description='段落ID')


class GujiAudioModel(BaseModel):
    """古籍听书音频模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    audio_id: int | None = Field(default=None, description='音频ID')
    book_id: int | None = Field(default=None, description='书目ID')
    chapter_id: int | None = Field(default=None, description='章节ID（0为全书音频）')
    audio_name: str | None = Field(default=None, description='音频名称')
    audio_url: str | None = Field(default=None, description='音频地址')
    duration_sec: int | None = Field(default=None, description='时长（秒）')


class GujiBookshelfModel(BaseModel):
    """书架条目模型（含书目信息与阅读进度）"""

    model_config = ConfigDict(alias_generator=to_camel)

    shelf_id: int | None = Field(default=None, description='书架ID')
    book_id: int | None = Field(default=None, description='书目ID')
    book_name: str | None = Field(default=None, description='书名')
    author: str | None = Field(default=None, description='作者')
    dynasty: str | None = Field(default=None, description='朝代')
    category: str | None = Field(default=None, description='分类')
    cover: str | None = Field(default=None, description='封面')
    chapter_count: int | None = Field(default=None, description='章节数')
    last_chapter_id: int | None = Field(default=None, description='最后阅读章节ID')
    last_chapter_name: str | None = Field(default=None, description='最后阅读章节名')
    last_paragraph_id: int | None = Field(default=None, description='最后阅读段落ID')
    read_time: ApiUtcDateTime | None = Field(default=None, description='最近阅读时间')


class GujiHistoryModel(BaseModel):
    """阅读历史条目模型"""

    model_config = ConfigDict(alias_generator=to_camel)

    history_id: int | None = Field(default=None, description='历史ID')
    book_id: int | None = Field(default=None, description='书目ID')
    book_name: str | None = Field(default=None, description='书名')
    author: str | None = Field(default=None, description='作者')
    chapter_id: int | None = Field(default=None, description='章节ID')
    chapter_name: str | None = Field(default=None, description='章节名')
    paragraph_id: int | None = Field(default=None, description='段落ID')
    read_time: ApiUtcDateTime | None = Field(default=None, description='阅读时间')
