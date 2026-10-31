/**
 * 识典古籍 - 阅读设置本地存储
 *
 * 修改记录:
 * 25-01-01  创建
 */

const STORAGE_KEY = 'guji_reader_setting'

/** 默认阅读设置 */
export const DEFAULT_READER_SETTING =
{
  fontSize: 32,
  lineHeight: 1.8,
  bgColor: '#f7f1e4',
  showTranslate: true,
  showAnnotation: true,
  traditional: false,
  vertical: false,
  night: false
}

/**
 * 读取本地阅读设置
 * @returns {Object} 设置对象
 */
export function loadReaderSetting()
{
  const saved = uni.getStorageSync(STORAGE_KEY)
  return { ...DEFAULT_READER_SETTING, ...(saved || {}) }
}

/**
 * 保存阅读设置到本地
 * @param {Object} setting 设置对象
 */
export function saveReaderSetting(setting)
{
  uni.setStorageSync(STORAGE_KEY, { ...DEFAULT_READER_SETTING, ...setting })
}

export default { loadReaderSetting, saveReaderSetting }
