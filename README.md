# 识典古籍重建平台（shidianguji-rebuild）

基于 **REA 反编译分析** + **prjtmpl（uni-app Vue3）前端** + **RuoYi-FastAPI 后端** 完整重建的识典古籍阅读平台。含古籍书目浏览、分类/朝代筛选、章节目录、阅读器（段落分页/上下章切换/阅读进度上报）、书架、阅读历史、听书音频展示、登录鉴权。

## 一、技术架构

| 层 | 技术 | 说明 |
|---|---|---|
| 前端 | uni-app + Vue3 + uview-plus + pinia + axios | 基于 prjtmpl 模板，8 页面四 Tab，全部遵循 uniapp-coding-standards |
| 后端 | RuoYi-FastAPI（FastAPI + SQLAlchemy + MariaDB + Redis） | 新增 module_guji 业务模块（6 表 10 接口） |
| 反编译分析 | REA v6.8.0 + JADX 1.5.1 | 识典古籍 APK v5.1.0 全量反编译，产出分析报告 |

## 二、目录结构

```
shidianguji-rebuild/
├── README.md                     # 本文件
├── docs/
│   ├── 识典古籍反编译分析报告.md   # 反编译分析报告（API/Bridge/模块/重建方案）
│   └── rea-env.sh                # REA 工具链环境脚本
├── frontend/                     # prjtmpl 前端工程（uni-app Vue3）
│   ├── src/pages.json            # 8 页面 + 四 Tab 路由
│   ├── src/pages/                # 首页/书架/分类/我的 + 登录/详情/阅读器/历史
│   ├── src/utils/gujiApi.js      # 后端 API 封装（11 个方法，token 注入）
│   └── ...
└── backend/                      # RuoYi-FastAPI 后端工程
    ├── module_guji/              # 古籍业务模块（controller/dao/service/entity 五层）
    ├── sql/guji.sql              # 6 张古籍业务表 + 示例数据（公版古籍）
    ├── sql/ruoyi-fastapi.sql     # RuoYi 基础 54 表
    └── ...
```

## 三、后端启动

前置：Python 3.10+、MariaDB 10.6+、Redis 6+。

```bash
cd backend
# 1. 创建虚拟环境并安装依赖
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
# 2. 初始化数据库（root 密码按需修改）
mysql -uroot -p < sql/ruoyi-fastapi.sql   # 54 张 RuoYi 表
mysql -uroot -p ruoyi-fastapi < sql/guji.sql  # 6 张古籍业务表 + 数据
# 3. 关闭登录验证码（sys.account.captchaEnabled=false）
mysql -uroot -p ruoyi-fastapi -e "UPDATE sys_config SET config_value='false' WHERE config_key='sys.account.captchaEnabled';"
# 4. 启动
cp .env.dev.example .env.dev   # 按需修改 DB_SOURCES / REDIS_DATABASE / APP_PORT
APP_ENV=dev python app.py      # 默认 127.0.0.1:9099
```

> 注：Redis < 7 时需在 server.py 的 `_start_background_tasks` 中跳过
> `LogAggregatorService.consume_stream`（Redis 6 不支持 XAUTOCLAIM）。

测试账号：`admin / admin123`

## 四、前端启动

前置：Node 16+（推荐 20/22）。

```bash
cd frontend
npm install --legacy-peer-deps    # 解决 vite@4 与 @uni-helper/axios-adapter 的 peer 冲突
npm run dev:h5                    # H5 调试（默认 http://127.0.0.1:8080）
npm run build:h5                  # H5 构建（产物 dist/build/h5）
```

API 基址在 `src/utils/gujiApi.js` 的 `BASE_URL`，默认 `http://127.0.0.1:9099`，
H5 调试时浏览器与后端需同机可达（后端已配置 CORS 放行）。

## 五、后端接口清单（已实测）

| 方法 | 路径 | 说明 | 鉴权 |
|---|---|---|---|
| POST | /login | 登录（OAuth2 表单，验证码已关） | 否 |
| GET | /getInfo | 当前用户信息 | Bearer |
| GET | /guji/book/page | 书目分页（bookName/category/dynasty 筛选） | 否 |
| GET | /guji/book/{bookId} | 书目详情 | 否 |
| GET | /guji/book/{bookId}/chapters | 章节目录 | 否 |
| GET | /guji/chapter/{chapterId}/paragraphs | 段落分页（pageNum/pageSize） | 否 |
| GET | /guji/bookshelf | 我的书架 | Bearer |
| POST | /guji/bookshelf | 加入书架 {bookId} | Bearer |
| DELETE | /guji/bookshelf/{bookId} | 移出书架 | Bearer |
| GET | /guji/history | 阅读历史 | Bearer |
| POST | /guji/history | 上报进度 {bookId,chapterId,paragraphId} | Bearer |
| GET | /guji/audio/{bookId} | 听书音频列表 | 否 |

## 六、验证结果

- 后端 12 个接口全部 curl 实测通过（含登录态书架/历史/进度上报、未登录 401 拦截）。
- 前端 H5 构建通过；浏览器真实走查 8 个页面全通过：
  首页书目列表 → 分类双筛选 → 书目详情（章节/音频）→ 阅读器（上下章切换）→
  登录（admin/admin123）→ 书架（加入/移出）→ 阅读进度上报 → 历史记录展示。

## 七、数据说明

示例古籍为公版内容（论语/道德经/三字经/千字文/诗经/孟子），
由 guji.sql 一次性灌入，可直接用于演示与二次开发。
