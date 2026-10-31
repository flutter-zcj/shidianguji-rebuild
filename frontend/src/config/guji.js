/**
 * 识典古籍 - 服务端配置
 *
 * 修改记录:
 * 25-01-01  创建
 */

// 后端服务基础地址（RuoYi-FastAPI + module_guji）
// 可用 .env 中 VITE_GUJI_BASE_URL 覆盖；置空则走 vite devServer 代理（见 vite.config.ts）
const ENV_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_GUJI_BASE_URL) || ''

export const GUJI_BASE_URL = ENV_BASE_URL || 'http://127.0.0.1:9099'

// 古籍业务接口前缀，与后端 module_guji controller 保持一致
export const GUJI_API_PREFIX = '/api/ancientlib'

// 调试用户ID：通过 X-User-Id 头模拟登录态，0 表示游客
export const GUJI_DEBUG_USER_ID = 1

export default {
  GUJI_BASE_URL,
  GUJI_API_PREFIX,
  GUJI_DEBUG_USER_ID
}
