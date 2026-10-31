# 识典古籍（uni-app 前端）

基于 [prjtmpl](https://github.com/flutter-zcj/prjtmpl) 模板工程实现的「识典古籍」App 前端，还原原 Android App 的页面结构与交互。

## 一、运行

```bash
npm install --registry=https://registry.npmmirror.com

# H5 开发（vite devServer 已代理 /api/ancientlib → 127.0.0.1:9099）
npm run dev:h5

# H5 构建
npm run build:h5          # 产物 dist/build/h5

# 本地预览（静态服务 + 后端代理）
python3 scripts/serve_h5.py --port 8080 --backend http://127.0.0.1:9099
# 打开 http://127.0.0.1:8080
```

后端须先启动：`cd ../../ruoyi-fastapi-backend/ruoyi-fastapi-backend && python3 app.py`

## 二、后端地址

`src/config/guji.js`：

| 配置项 | 默认 | 说明 |
| --- | --- | --- |
| `GUJI_BASE_URL` | `http://127.0.0.1:9099` | 可用 `.env` 中 `VITE_GUJI_BASE_URL` 覆盖；置空走 vite 代理 |
| `GUJI_API_PREFIX` | `/api/ancientlib` | 与后端 controller 前缀一致 |
| `GUJI_DEBUG_USER_ID` | `1` | 通过 `X-User-Id` 头模拟登录态，0 表示游客 |

真机/小程序请在 `.env` 里写局域网地址：`VITE_GUJI_BASE_URL=http://192.168.x.x:9099`

## 三、页面清单（`src/pages/guji/`）

| 页面 | 路径 | 对应原 App 页面 | 能力 |
| --- | --- | --- | --- |
| 首页 | `index/index` | Lynx `home` | Banner、四部分类/名句/听书/讲书入口、今日推荐、每日名句 |
| 书架 | `shelf/shelf` | Lynx `shelf` | 书架列表、最近阅读、移出书架、继续阅读 |
| 分类 | `category/category` | Lynx `category` | 经史子集左侧导航 + 分类下书籍 |
| 我的 | `mine/mine` | Lynx `logged/myReadPage` | 等级/打卡/贡献/收藏统计与功能入口 |
| 书籍详情 | `book/book` | H5 `bookDetail` | 简介、目录、整理校对、入架、听书/讲书标记 |
| 阅读器 | `reader/reader` | H5 `read` | 原文/译文/注疏同段渲染、目录抽屉、书签、笔记、进度上报、AI |
| 搜索 | `search/search` | H5 `search` | 古籍检索 + 原文检索双 Tab |
| 名句 | `quotation/quotation` | H5 `mingju` | 名句推荐 / 我的收藏（`?mine=1`）、收藏切换 |
| 笔记与书签 | `notes/notes` | H5 `myNote` | 按书聚合书签与笔记，跳转章节、删除 |
| 我的书单 | `topic/topic` | H5 `topic` | 书单创建、关注、书单内书籍管理 |
| 通知 | `notice/notice` | Lynx `notice` | 系统通知列表 |
| 阅读设置 | `settings/settings` | H5 `readerSetting` | 字号/行距/背景/译文/注疏/繁体/竖排/夜间 |
| 听书 | `audio/audio` | Lynx `audio` | 听书与播客列表、音频播放、歌词 |
| 讲书 | `video/video` | Lynx `video` / `courseSeries` | 推荐视频、讲书系列与讲解列表、讲解搜索 |
| AI 问答 | `ai/ai` | H5 `ai` | 基于古籍库的智能问答 |

阅读设置存于本地 `guji_reader_setting`，由 `src/utils/gujiSetting.js` 统一读写。

## 四、接口层

`src/api/guji.js`：axios 封装 + 约 75 个接口函数，统一注入 `X-User-Id`，统一解包 `{code,msg,data}`。

## 五、TabBar

`src/pages.json` 配置 4 个 Tab：首页 / 书架 / 分类 / 我的，图标位于 `src/static/tab/`。

## 六、git commit 提交说明

```
  git commit -m "type: 提交说明"
  如: git commit -m "fix: 修复bug2135中不能删除用户"
```

type 取值：feat / fix / docs / style / refactor / perf / test / chore / revert。
