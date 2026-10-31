/**
 * 模块名称：gujiApi
 * 功能说明：识典古籍阅读平台 API 请求封装（基于 uni.request，统一处理登录态与响应包）
 * 研发时间：2026/10/31
 * 研发人员：Doubao
 *
 * 变量说明：
 * @data {String} BASE_URL   - 后端服务基址
 *
 * 事件说明：
 * @event request            - 通用请求方法，封装 uni.request 与 token 注入
 * @event login              - 用户登录（OAuth2 表单）
 * @event getInfo            - 获取当前登录用户信息
 * @event getBookPage        - 古籍书目分页列表
 * @event getBookDetail      - 古籍书目详情
 * @event getChapters        - 章节目录
 * @event getParagraphs      - 章节段落分页
 * @event getBookshelf       - 我的书架
 * @event addBookshelf       - 加入书架
 * @event deleteBookshelf    - 移出书架
 * @event getHistory         - 阅读历史
 * @event addHistory         - 上报阅读进度
 * @event getAudio           - 听书音频列表
 */

/**
 * 修改时间       人员        说明
 */

const BASE_URL = 'http://127.0.0.1:9099'

const TOKEN_KEY = 'guji_token'

/**
 * 通用请求方法，封装 uni.request 与 token 注入
 * @param {Object} options   - 请求配置（url/method/data/form）
 * @returns {Promise<Object>} 后端响应对象 { code, msg, data, success }
 */
const request = (options) =>
  new Promise((resolve, reject) => {
    const token = uni.getStorageSync(TOKEN_KEY)
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': options.form ? 'application/x-www-form-urlencoded' : 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success: (res) => {
        if (res.statusCode === 401) {
          uni.removeStorageSync(TOKEN_KEY)
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(res)
        }
      },
      fail: reject,
    })
  })

/**
 * 用户登录（OAuth2 表单）
 * @param {String} username  - 用户名
 * @param {String} password  - 密码
 * @returns {Promise<Object>} 登录响应（含 token）
 */
export const login = (username, password) =>
  request({
    url: '/login',
    method: 'POST',
    form: true,
    data: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
  })

/**
 * 获取当前登录用户信息
 * @returns {Promise<Object>} 用户信息响应
 */
export const getInfo = () => request({ url: '/getInfo', method: 'GET' })

/**
 * 古籍书目分页列表
 * @param {Object} params    - 查询参数（pageNum/pageSize/bookName/category/dynasty）
 * @returns {Promise<Object>} 分页响应
 */
export const getBookPage = (params) => request({ url: '/guji/book/page', method: 'GET', data: params })

/**
 * 古籍书目详情
 * @param {Number} bookId    - 书目ID
 * @returns {Promise<Object>} 书目详情响应
 */
export const getBookDetail = (bookId) => request({ url: `/guji/book/${bookId}`, method: 'GET' })

/**
 * 章节目录
 * @param {Number} bookId    - 书目ID
 * @returns {Promise<Object>} 章节列表响应
 */
export const getChapters = (bookId) => request({ url: `/guji/book/${bookId}/chapters`, method: 'GET' })

/**
 * 章节段落分页
 * @param {Number} chapterId - 章节ID
 * @param {Number} pageNum   - 页码
 * @param {Number} pageSize  - 每页条数
 * @returns {Promise<Object>} 段落分页响应
 */
export const getParagraphs = (chapterId, pageNum = 1, pageSize = 20) =>
  request({ url: '/guji/chapter/' + chapterId + '/paragraphs', method: 'GET', data: { pageNum, pageSize } })

/**
 * 我的书架
 * @returns {Promise<Object>} 书架列表响应
 */
export const getBookshelf = () => request({ url: '/guji/bookshelf', method: 'GET' })

/**
 * 加入书架
 * @param {Number} bookId    - 书目ID
 * @returns {Promise<Object>} 操作结果响应
 */
export const addBookshelf = (bookId) =>
  request({ url: '/guji/bookshelf', method: 'POST', data: { bookId } })

/**
 * 移出书架
 * @param {Number} bookId    - 书目ID
 * @returns {Promise<Object>} 操作结果响应
 */
export const deleteBookshelf = (bookId) =>
  request({ url: `/guji/bookshelf/${bookId}`, method: 'DELETE' })

/**
 * 阅读历史
 * @returns {Promise<Object>} 历史列表响应
 */
export const getHistory = () => request({ url: '/guji/history', method: 'GET' })

/**
 * 上报阅读进度
 * @param {Object} data      - 进度数据（bookId/chapterId/paragraphId）
 * @returns {Promise<Object>} 操作结果响应
 */
export const addHistory = (data) => request({ url: '/guji/history', method: 'POST', data })

/**
 * 听书音频列表
 * @param {Number} bookId    - 书目ID
 * @returns {Promise<Object>} 音频列表响应
 */
export const getAudio = (bookId) => request({ url: `/guji/audio/${bookId}`, method: 'GET' })
