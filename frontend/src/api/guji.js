import axios from 'axios'
import { GUJI_BASE_URL, GUJI_API_PREFIX, GUJI_DEBUG_USER_ID } from '@/config/guji.js'

/**
 * 识典古籍 - 接口封装
 *
 * 路径与方法与原App保持一致（来自反编译提取的 API 注册表）：
 *   /api/ancientlib/read/...   阅读、书架、书签、笔记
 *   /api/ancientlib/app/...    首页、讲书、视频
 *   /api/ancientlib/dict/...   字典、实体
 */

const request = axios.create({
  baseURL: GUJI_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// 用户ID（登录后写入，默认调试用户）
let userId = uni.getStorageSync('guji_user_id') || GUJI_DEBUG_USER_ID

export function setGujiUserId(id)
{
  userId = id
  uni.setStorageSync('guji_user_id', id)
}

export function getGujiUserId()
{
  return userId
}

request.interceptors.request.use((config) =>
{
  config.headers['X-User-Id'] = String(userId)
  return config
})

/**
 * 统一取数：后端统一封装为 {code, msg, data}
 * @param {Object} promise
 * @returns {Promise<Object>}
 */
async function unwrap(promise)
{
  const res = await promise
  const body = res.data || {}
  if (body.code !== undefined && body.code !== 200)
    throw new Error(body.msg || '接口请求失败')
  return body.data ?? body
}

const get = (url, params) => unwrap(request.get(url, { params }))
const post = (url, data) => unwrap(request.post(url, data || {}))

/* ------------------------------ 书籍 ------------------------------ */

export const getBookCount = () => get(`${GUJI_API_PREFIX}/read/book/count`)

export const getBookList = (params) =>
  post(`${GUJI_API_PREFIX}/read/book-by-category/list`, params)

export const batchGetBook = (bookIds) =>
  post(`${GUJI_API_PREFIX}/read/book/batch-get/`, { bookIds })

export const getBookDetail = (bookId, needCatalog = 1) =>
  post(`${GUJI_API_PREFIX}/read/reader-book/get/`, { bookId, needCatalog })

export const getVolumeDetail = (volumeId) =>
  get(`${GUJI_API_PREFIX}/read/get/volume/`, { volumeId })

export const getBookParagraphs = (params) =>
  post(`${GUJI_API_PREFIX}/read/book/paragraphs/v3/`, params)

export const getBookContributor = (bookId, pageNum = 1, pageSize = 20) =>
  get(`${GUJI_API_PREFIX}/read/book/contributor/list/`, { bookId, pageNum, pageSize })

export const getBookCorrector = (bookId, pageNum = 1, pageSize = 20) =>
  get(`${GUJI_API_PREFIX}/read/book/corrector/list/`, { bookId, pageNum, pageSize })

export const getRecommendBook = (pageNum = 1, pageSize = 10) =>
  get(`${GUJI_API_PREFIX}/read/recommend-book/get/`, { pageNum, pageSize })

/* ------------------------------ 分类 ------------------------------ */

export const getCategoryTree = () => get(`${GUJI_API_PREFIX}/read/get/category-tree/`)

export const getBookByCategory = (cateId, pageNum = 1, pageSize = 20) =>
  post(`${GUJI_API_PREFIX}/read/book-by-category/list`, { cateId, pageNum, pageSize })

export const getCategoryBoard = (cateId) =>
  post(`${GUJI_API_PREFIX}/read/category-board-detail/get/`, { cateId })

/* ------------------------------ 搜索 ------------------------------ */

export const searchBook = (queryText, pageNum = 1, pageSize = 20) =>
  post(`${GUJI_API_PREFIX}/read/search/book/v1`, { queryText, pageNum, pageSize })

export const searchParagraph = (params) =>
  post(`${GUJI_API_PREFIX}/read/search/paragraph/v1/`, params)

export const getSearchRecommendWord = () =>
  post(`${GUJI_API_PREFIX}/read/search-recommend-word/get/`)

/* ------------------------------ 首页 ------------------------------ */

export const getHomepage = () => post(`${GUJI_API_PREFIX}/read/app/homepage/v4/`)

export const getHomepageUser = () => post(`${GUJI_API_PREFIX}/read/app/homepage-user/`)

export const getHomepageBanner = () => get(`${GUJI_API_PREFIX}/read/homepage-banner/get/`)

export const getFeedBook = (pageNum = 1, pageSize = 20) =>
  post(`${GUJI_API_PREFIX}/read/app/feed-book/`, { pageNum, pageSize })

/* ------------------------------ 书架 ------------------------------ */

export const listShelf = (params) =>
  post(`${GUJI_API_PREFIX}/read/bookshelf/list-all/v4/`, params)

export const addShelf = (bookId, shelfBizType = 'book') =>
  post(`${GUJI_API_PREFIX}/read/bookshelf/add/`, { bookId, shelfBizType })

export const deleteShelf = (bookIds, shelfBizType = 'book') =>
  post(`${GUJI_API_PREFIX}/read/bookshelf/batch-delete/v4/`, { bizIds: bookIds, shelfBizType })

export const checkShelf = (bookIds, shelfBizType = 'book') =>
  post(`${GUJI_API_PREFIX}/read/bookshelf/batch-check/v4/`, { bizIds: bookIds, shelfBizType })

/* ------------------------------ 阅读历史 ------------------------------ */

export const reportHistory = (params) =>
  post(`${GUJI_API_PREFIX}/read/history/report/`, params)

export const getHistory = (bizId, shelfBizType = 'book') =>
  post(`${GUJI_API_PREFIX}/read/history/get/v4/`, { bizId, shelfBizType })

export const listHistory = (pageNum = 1, pageSize = 20, shelfBizType = 'book') =>
  post(`${GUJI_API_PREFIX}/read/history/list/v3/`, { pageNum, pageSize, shelfBizType })

export const deleteHistory = (bizIds, shelfBizType = 'book') =>
  post(`${GUJI_API_PREFIX}/read/history/batch-delete/v4/`, { bizIds, shelfBizType })

/* ------------------------------ 书签 / 笔记 ------------------------------ */

export const addBookmark = (params) => post(`${GUJI_API_PREFIX}/read/bookmark/add/`, params)

export const listBookmark = (bookId) =>
  get(`${GUJI_API_PREFIX}/read/bookmark/list/`, { bookId })

export const deleteBookmark = (bookmarkId) =>
  post(`${GUJI_API_PREFIX}/read/bookmark/del/`, { bookmarkId })

export const addReview = (params) => post(`${GUJI_API_PREFIX}/read/review/add/`, params)

export const listReview = (bookId) =>
  get(`${GUJI_API_PREFIX}/read/review/personal-list/`, { bookId })

export const deleteReview = (reviewId) =>
  post(`${GUJI_API_PREFIX}/read/review/del/`, { reviewId })

export const listChapterReview = (bookId, chapterId) =>
  get(`${GUJI_API_PREFIX}/read/review/chapter-list/`, { bookId, chapterId })

/* ------------------------------ 收藏 ------------------------------ */

export const listFavorite = (bizType = 'quotation', pageSize = 20, nextPageToken = 0) =>
  post(`${GUJI_API_PREFIX}/read/favorites/basic/page/`, { bizType, pageSize, nextPageToken })

export const addFavorite = (bizId, bizType = 'quotation') =>
  post(`${GUJI_API_PREFIX}/read/favorites/batch-add/`, { bizIds: [bizId], bizType })

export const delFavorite = (bizId, bizType = 'quotation') =>
  post(`${GUJI_API_PREFIX}/read/favorites/batch-del/`, { bizIds: [bizId], bizType })

export const countFavorite = (bizType) =>
  post(`${GUJI_API_PREFIX}/read/favorites/count/`, { bizType })

/* ------------------------------ 名句 ------------------------------ */

export const listQuotation = (params) =>
  post(`${GUJI_API_PREFIX}/read/book/quotation-basic/page/`, params)

export const getQuotationDetail = (quotationId) =>
  get(`${GUJI_API_PREFIX}/read/mingju-detail/get`, { quotationId })

export const listQuotationCategory = () =>
  get(`${GUJI_API_PREFIX}/read/mingju-category/get`)

export const recommendQuotation = (pageSize = 20, nextPageToken = 0) =>
  post(`${GUJI_API_PREFIX}/read/app/recommend-quotation/page/`, { pageSize, nextPageToken })

/* ------------------------------ 话题书单 ------------------------------ */

export const listTopic = (pageNum = 1, pageSize = 20) =>
  get(`${GUJI_API_PREFIX}/read/topic/list/`, { pageNum, pageSize })

export const getTopicDetail = (topicId) =>
  get(`${GUJI_API_PREFIX}/read/topic/get/`, { topicId })

export const saveTopic = (params) => post(`${GUJI_API_PREFIX}/read/topic/save/`, params)

export const createTopic = (params) => post(`${GUJI_API_PREFIX}/read/topic/create/`, params)

export const listPersonalTopic = (pageNum = 1, pageSize = 20) =>
  get(`${GUJI_API_PREFIX}/read/topic/personal-list/`, { pageNum, pageSize })

export const followTopic = (topicId) =>
  post(`${GUJI_API_PREFIX}/read/topic/follow/`, { topicId })

export const unfollowTopic = (topicId) =>
  post(`${GUJI_API_PREFIX}/read/topic/unfollow/`, { topicId })

export const listTopicBook = (topicId) =>
  get(`${GUJI_API_PREFIX}/read/topic/book/list/`, { topicId })

export const addTopicBook = (topicId, bookId) =>
  post(`${GUJI_API_PREFIX}/read/topic/book/add/`, { topicId, bookId })

export const deleteTopicBook = (topicId, bookId) =>
  post(`${GUJI_API_PREFIX}/read/topic/book/delete/`, { topicId, bookId })

/* ------------------------------ 做过标记的书 ------------------------------ */

export const listMarkedBook = () => get(`${GUJI_API_PREFIX}/read/marked-book/list/`)

/* ------------------------------ 字典 / 实体 ------------------------------ */

export const getDictionary = (word) =>
  get(`${GUJI_API_PREFIX}/read/dictionary/get/`, { word })

export const getCharDetail = (char) => post(`${GUJI_API_PREFIX}/dict/char-detail`, { char })

export const searchCharByRad = (rad, pageNum = 1, pageSize = 50) =>
  get(`${GUJI_API_PREFIX}/dict/search-char-by-rad`, { rad, pageNum, pageSize })

export const getEntityDetail = (entityId) =>
  get(`${GUJI_API_PREFIX}/read/entity/get`, { entityId })

/* ------------------------------ 听书 / 播客 ------------------------------ */

export const getBookAudio = (bookId) => post(`${GUJI_API_PREFIX}/read/book-audio/get`, { bookId })

export const getAudioLyric = (audioId) =>
  post(`${GUJI_API_PREFIX}/read/audio-lyric/get`, { audioId })

export const listPodcast = (pageNum = 1, pageSize = 20) =>
  post(`${GUJI_API_PREFIX}/app/podcast-book/list/v2/`, { pageNum, pageSize })

export const listListeningBook = (pageNum = 1, pageSize = 20) =>
  post(`${GUJI_API_PREFIX}/app/listening-book/list/`, { pageNum, pageSize })

/* ------------------------------ 视频 / 讲书 ------------------------------ */

export const listVideo = (pageNum = 1, pageSize = 20) =>
  post(`${GUJI_API_PREFIX}/read/app/recommend-video/page/`, { pageNum, pageSize })

export const listCourseSeries = (pageNum = 1, pageSize = 20) =>
  get(`${GUJI_API_PREFIX}/app/explain/course-series/list`, { pageNum, pageSize })

export const getCourseDetail = (seriesId) =>
  post(`${GUJI_API_PREFIX}/app/explain/course-series/get-course-detail-v2`, { seriesId })

export const listCourseExplain = (seriesId) =>
  post(`${GUJI_API_PREFIX}/app/explain/course-explain/list`, { seriesId })

export const searchExplain = (keyword) =>
  post(`${GUJI_API_PREFIX}/app/explain/search`, { keyword })

/* ------------------------------ 用户 ------------------------------ */

export const getPreferences = () => post(`${GUJI_API_PREFIX}/read/app/preferences/get/`)

export const setPreferences = (preferences) =>
  post(`${GUJI_API_PREFIX}/read/app/preferences/set/`, { preferences })

export const getPreferenceOptions = () =>
  get(`${GUJI_API_PREFIX}/read/app/preferences/options/`)

export const readerClock = (bookId) =>
  post(`${GUJI_API_PREFIX}/read/reader-clocks/clock/`, { bookId })

export const getClockInfo = () => post(`${GUJI_API_PREFIX}/read/app/my-reading-clock-info/get/`)

export const getUserLevel = () => get(`${GUJI_API_PREFIX}/read/user-level/get/`)

export const getNoticeList = (pageNum = 1, pageSize = 20) =>
  get(`${GUJI_API_PREFIX}/read/notice/list`, { pageNum, pageSize })

export const getContribution = () => post(`${GUJI_API_PREFIX}/read/contribution/user/`)

export const assistantChat = (question, bookId) =>
  post(`${GUJI_API_PREFIX}/read/assistant/chat/`, { question, bookId })

export const assistantHistory = (sessionId) =>
  get(`${GUJI_API_PREFIX}/read/assistant/history/`, { sessionId })

export const submitFeedback = (params) => post(`${GUJI_API_PREFIX}/read/feedback/`, params)

export const genShortLink = (bizId) => post(`${GUJI_API_PREFIX}/read/gen-short-link/`, { bizId })

export default {
  getBookCount,
  getBookList,
  batchGetBook,
  getBookDetail,
  getBookParagraphs,
  getCategoryTree,
  searchBook,
  searchParagraph,
  getHomepage,
  listShelf,
  addShelf,
  deleteShelf,
  checkShelf,
  reportHistory,
  getHistory,
  listHistory,
  addBookmark,
  listBookmark,
  addReview,
  listReview,
  listFavorite,
  addFavorite,
  delFavorite,
  listQuotation,
  getQuotationDetail,
  listTopic,
  getTopicDetail,
  getDictionary,
  getBookAudio,
  listPodcast,
  listVideo,
  listCourseSeries,
  getCourseDetail,
  getPreferences,
  setPreferences,
  readerClock,
  getUserLevel,
  assistantChat
}
