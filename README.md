# 识典古籍重建平台（shidianguji-rebuild）

基于 **REA 反编译分析** + **prjtmpl（uni-app Vue3）前端** + **RuoYi-FastAPI 后端** 完整重建的识典古籍阅读平台。

- 线上地址：<https://60.204.248.157:8081/guji/>（自签证书，浏览器点"继续访问"）
- 数据规模：**244 本真实古籍 / 15039 章 / 691241 段 / 3232 万字**

## 一、技术架构

| 层 | 技术 | 说明 |
|---|---|---|
| 前端 | uni-app + Vue3 + Vite + uview-plus + z-paging + axios | 基于 [prjtmpl](https://github.com/flutter-zcj/prjtmpl) 模板，**15 个页面 + 4 个 TabBar** |
| 后端 | RuoYi-FastAPI（FastAPI + SQLAlchemy Async + PostgreSQL + Redis） | 新增 `module_guji`：**41 张表 / 10 个 controller / 218 条路由**，路径严格对齐原 App |
| 反编译 | REA + 自研 DEX 解析器 + JADX 1.5.2 + Gecko 离线包解压 | 识典古籍 APK 全量反编译：Lynx 27 页 / H5 31 页 / 路由表 54 条 / 557 条接口 / 57 个 JSBridge |

后端接口前缀 `/api/ancientlib/**`，与原 App 保持一致（如 `/read/book/paragraphs/v3/`、`/read/bookshelf/list-all/v4/`、`/app/explain/course-series/get-course-detail-v2`）。

## 二、目录结构

```
shidianguji-rebuild/
├── README.md                          # 本文件
├── docs/
│   ├── 识典古籍反编译分析报告.md        # 反编译分析报告（API / Bridge / 模块 / 重建方案）
│   ├── 识典古籍页面与实体模型报告.md    # 页面清单、实体字段、阅读器交互对照
│   ├── 交付说明.md                    # 功能对照与验证记录
│   ├── 部署说明.md                    # 服务器部署（nginx + systemd + 数据迁移）
│   └── rea-env.sh                    # REA 工具链环境脚本
├── frontend/                          # prjtmpl 前端工程（uni-app Vue3）
│   ├── src/pages.json                 # 15 条路由 + 4 个 TabBar
│   ├── src/pages/guji/                # 首页/书架/分类/我的/详情/阅读器/搜索/名句/
│   │                                  # 笔记/书单/通知/设置/听书/讲书/AI
│   ├── src/api/guji.js                # 后端 API 封装（约 70 个方法）
│   ├── src/config/guji.js             # 服务地址、API 前缀、调试用户
│   ├── src/utils/gujiSetting.js       # 阅读设置（字号/行距/背景/译注/繁简/夜间）
│   ├── src/static/tab/                # TabBar 图标
│   └── scripts/serve_h5.py            # H5 静态服务 + 后端代理（本地调试用）
└── backend/                           # RuoYi-FastAPI 后端工程
    └── module_guji/                   # 古籍业务模块
        ├── controller/                # 10 个控制器（book/bookshelf/history/note/topic/
        │                              # search/dict/media/user/quotation）
        ├── service/  dao/             # 业务层 / 数据层（内容、用户、媒体三域）
        ├── entity/do/                 # 41 张表 ORM 模型
        ├── entity/vo/                 # 请求/响应模型（驼峰别名）
        ├── aspect/                    # guji_auth（游客/令牌/JWT）、guji_session（自动提交）
        └── scripts/                   # init_guji_db / migrate_real_data / polish_data /
                                       # seed_quotations（建表与数据迁移）
```

## 三、功能清单

| 模块 | 页面 | 能力 |
|---|---|---|
| 首页 | `index/index` | Banner、推荐位、每日名句、功能入口 |
| 书架 | `shelf/shelf` | 书架列表、最近阅读、移出书架 |
| 分类 | `category/category` | 经史子集左侧导航 + 书籍列表 |
| 我的 | `mine/mine` | 等级/打卡/贡献/收藏 + 各功能入口 |
| 书籍详情 | `book/book` | 简介、目录、整理者、加入书架 |
| 阅读器 | `reader/reader` | 原文/译文/注疏同屏、目录抽屉、书签、笔记、进度上报 |
| 搜索 | `search/search` | 古籍检索 + 原文检索双 Tab |
| 名句 | `quotation/quotation` | 名句推荐 / 我的收藏 |
| 笔记 | `notes/notes` | 书签与笔记双 Tab，按书聚合 |
| 书单 | `topic/topic` | 书单创建、关注、书籍管理 |
| 通知 | `notice/notice` | 系统通知列表（含未读标记） |
| 设置 | `settings/settings` | 字号/行距/背景/译文/注疏/繁体/竖排/夜间 |
| 听书 | `audio/audio` | 听书 + 播客双 Tab，音频播放与歌词 |
| 讲书 | `video/video` | 推荐视频 + 讲书系列 → 讲解列表 |
| AI | `ai/ai` | 古籍问答（检索式回答） |

## 四、本地启动

### 后端（Python 3.10+ / PostgreSQL / Redis）

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements-pg.txt        # 需 asyncpg（PostgreSQL 异步驱动）
python -m module_guji.scripts.init_guji_db  # 建 guji_* 表 + 示例数据（4 本书）
APP_ENV=dev python app.py                 # 默认 127.0.0.1:9099
```

DB/Redis 在 `.env.dev` 中配置（`DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME`、`REDIS_*`）。
调试态可用 `X-User-Id: 1` 请求头直接指定用户，无需登录。

### 前端（Node 16+，推荐 20/22）

```bash
cd frontend
npm install --registry=https://registry.npmmirror.com
npm run dev:h5                            # H5 调试
VITE_GUJI_BASE_URL=/guji-api npm run build:h5   # 构建（API 走同源前缀）
python3 scripts/serve_h5.py --port 8080 --backend http://127.0.0.1:9099
```

`src/config/guji.js` 的 `GUJI_BASE_URL` 可用环境变量 `VITE_GUJI_BASE_URL` 覆盖。

## 五、服务器部署

见 [docs/部署说明.md](docs/部署说明.md)。要点：

- 形态 A：挂进既有 `zbcx-web`（9099），`/api/ancientlib/**` 与既有 `/guji/**` 路由并存
- nginx：`/guji/` 静态站点 + `/guji-api/` 反代到 9099
- 数据：从 `gj_*` 源表迁移到 `guji_*`，并执行 `polish_data.sql` 重建章节目录

## 六、验证结果

- 后端 218 条路由全部注册，`/api/ancientlib` 核心链路 curl 实测通过
  （书目/分类/详情/正文/书架/书签/笔记/书单/收藏/偏好/打卡/进度/AI/查字/音频/视频）
- 前端 H5 构建通过，15 个页面真浏览器走查：**0 个 JS 报错、0 个 4xx/5xx**
- 真实数据验收：《论语》正确拆出「学而第一 / 为政第二…」21 章，名句取自书中真实句子

## 七、已知边界

- **听书 / 讲书为空态**：库内无音频视频数据，页面与接口本身可用
- AI 助手为检索式回答（未接大模型），需接 LLM 时替换 `service/guji_user_service.py` 的 `assistant_chat`
- 竖排排版开关已预留，渲染层未实现竖排布局
- 登录为 `X-User-Id` 调试态，未做真实账号体系与第三方登录
- 部分书籍章节名为首句截断（≤24 字），非标准篇名

## 八、数据来源

古籍正文来自服务器 `zbcx_sj` 库 `gj_*` 表（公版古籍数字化文本），
经 `migrate_real_data.sql` / `polish_data.sql` 迁移与清洗后入库。
