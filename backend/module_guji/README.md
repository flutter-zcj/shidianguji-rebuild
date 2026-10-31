# module_guji（识典古籍后端模块）

基于 **RuoYi-FastAPI** 实现的「识典古籍」服务端模块，接口路径、请求/响应字段对齐原 Android App 真实抓包与反编译结果（`/api/ancientlib/**`）。

## 一、目录结构

```
module_guji/
├── aspect/                  # 鉴权与会话切面
│   ├── guji_auth.py         # GujiUserModel / resolve_user（X-User-Id > guji_<id> 令牌 > JWT > 游客）
│   └── guji_session.py      # GujiDbSession：yield 后自动 commit，异常 rollback
├── controller/              # 10 个控制器，227 个路由
│   ├── guji_book_controller.py        # 书籍/卷/章节/段落/分类/贡献者
│   ├── guji_bookshelf_controller.py   # 书架（list-all/v4、batch-add/v4、batch-check/v4 …）
│   ├── guji_history_controller.py     # 阅读历史与进度上报
│   ├── guji_note_controller.py        # 书签/笔记/划线书/页边注/通用收藏
│   ├── guji_quotation_controller.py   # 名句与名句分类
│   ├── guji_topic_controller.py       # 话题书单与书单内书籍
│   ├── guji_search_controller.py      # 古籍检索/原文检索/推荐词
│   ├── guji_dict_controller.py        # 字典字形/实体/实体引用/位置检索
│   ├── guji_media_controller.py       # 听书音频/播客/视频/讲书系列/课程讲解
│   └── guji_user_controller.py        # 首页/偏好/打卡/等级/通知/贡献/AI助手
├── dao/                     # 三域数据访问：content / user / media
├── entity/
│   ├── do/                  # 41 张表的 ORM 模型
│   └── vo/                  # 请求/响应模型（驼峰别名 GujiBaseModel）
├── service/                 # 业务服务层
└── scripts/init_guji_db.py  # 建表 + 示例数据
```

## 二、数据模型（41 张表）

| 域 | 表 |
| --- | --- |
| 内容 | `guji_book`（4 部/版本三元组）、`guji_volume`、`guji_chapter`、`guji_paragraph`（`content_type` 位标记：原文/译文/注疏/校勘同段下发）、`guji_category`、`guji_contributor`、`guji_quotation`、`guji_quotation_category`、`guji_entity`、`guji_entity_ref`、`guji_dict_char`、`guji_margin_note`、`guji_feedback` |
| 用户 | `guji_bookshelf`（`shelf_biz_type` 多用）、`guji_read_history`、`guji_bookmark`、`guji_review`、`guji_favorite`（`biz_type + biz_id` 通用收藏）、`guji_topic`、`guji_topic_book`、`guji_topic_follow`、`guji_user_preference`、`guji_user_clock`、`guji_user_level`、`guji_level_gift_order`、`guji_notice`、`guji_notice_read`、`guji_assistant_chat`、`guji_user_address`、`guji_user_tag` |
| 媒体 | `guji_audio`、`guji_audio_lyric`、`guji_video`、`guji_video_course`、`guji_course_series`、`guji_course_explain`、`guji_homepage_banner`、`guji_recommend`、`guji_preferences_tag`、`guji_preferences_tag_book`、`guji_team` |

## 三、启动

```bash
# 1. 依赖（PostgreSQL 异步驱动）
pip3 install -r requirements-pg.txt

# 2. 配置 .env.dev（示例）
#    DB_HOST=127.0.0.1  DB_PORT=15432  DB_USER=postgres  DB_PASSWORD=postgres  DB_DATABASE=ruoyi_fastapi
#    REDIS_HOST=127.0.0.1  REDIS_PORT=16379
#    APP_ROOT_PATH=''

# 3. 建表 + 示例数据（论语/道德经/史记/陶渊明集，各 4 章 × 若干段）
python3 -m module_guji.scripts.init_guji_db

# 4. 启动
cd ruoyi-fastapi-backend && python3 app.py     # 默认 9099
```

## 四、鉴权

调试期用请求头 `X-User-Id: 1` 模拟登录；生产可切到 `Authorization: Bearer guji_<id>` 或系统 JWT，见 `aspect/guji_auth.py`。

## 五、已验证链路

书籍总数 / 分类树 / 分类下书籍 / 书籍详情 / 章节正文 / 加入书架 / 书架列表 /
书签增删查 / 笔记增删查 / 书单创建与列表 / 名句收藏 / 偏好读写 / 阅读打卡 /
阅读进度上报与读取 / AI 问答 / 听书音频 / 讲书系列 / 视频列表 / 通知列表 / 查字。
