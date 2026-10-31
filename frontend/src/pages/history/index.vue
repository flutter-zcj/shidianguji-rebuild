<style lang="scss" scoped>
.history-page { display: flex; flex-direction: column; min-height: 100vh; background: #F8F6F1; }
.history-list { display: flex; flex-direction: column; padding: 24rpx; gap: 20rpx; }
.history-card { display: flex; padding: 24rpx; background: #FFFFFF; border-radius: 16rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06); }
.history-info { display: flex; flex: 1; flex-direction: column; justify-content: center; }
.history-name { font-size: 30rpx; color: #333333; font-weight: 600; }
.history-meta { font-size: 24rpx; color: #999999; margin-top: 10rpx; }
.empty-tip { display: flex; align-items: center; justify-content: center; height: 400rpx; font-size: 28rpx; color: #999999; }
</style>
<template>
  <!-- 🚀 页面主体 -->
  <view class="history-page">
    <!-- 🚀 历史列表 -->
    <view class="history-list">
      <view v-for="item in historyList" :key="item.historyId" class="history-card" @click="handleOpenReader(item)">
        <view class="history-info">
          <view class="history-name">{{ item.bookName }}</view>
          <view class="history-meta">{{ item.chapterName || '全书' }} · {{ formatTime(item.readTime) }}</view>
        </view>
      </view>
      <view v-if="historyList.length === 0 && !loading" class="empty-tip">暂无阅读记录</view>
    </view>
  </view>
</template>
<script>
/**
 * 组件名称：history
 * 功能说明：阅读历史页面，按时间倒序展示最近阅读记录，支持跳转继续阅读
 * 研发时间：2026/10/31
 * 研发人员：Doubao
 *
 * 变量说明：
 * @data {Array}   historyList - 阅读历史列表
 * @data {Boolean} loading     - 是否加载中
 *
 * 事件说明：
 * @event onShow           - 页面显示时拉取历史
 * @event onPullDownRefresh - 下拉刷新历史
 * @event handleOpenReader - 打开阅读器继续阅读
 * @event formatTime       - 格式化阅读时间
 * @event loadHistory      - 拉取阅读历史
 *
 * 插槽说明：
 */
/**
 * 修改时间       人员        说明
 */

import { getHistory } from '../../utils/gujiApi'

export default
{
  data()
  {
    return {
      historyList: [],
      loading: false,
    }
  },

  onShow()
  {
    /**
     * 页面显示时拉取历史
     */
    this.loadHistory()
  },

  onPullDownRefresh()
  {
    /**
     * 下拉刷新历史
     */
    this.loadHistory().finally(() => uni.stopPullDownRefresh())
  },

  methods:
  {
    /**
     * 打开阅读器继续阅读
     * @param {Object} item - 历史条目
     */
    handleOpenReader(item)
    {
      if (item.chapterId)
      {
        uni.navigateTo({
          url: `/pages/reader/index?bookId=${item.bookId}&chapterId=${item.chapterId}&paragraphId=${item.paragraphId || 0}`,
        })
      }
      else
      {
        uni.navigateTo({ url: `/pages/book/detail?bookId=${item.bookId}` })
      }
    },

    /**
     * 格式化阅读时间
     * @param {String} time - 时间字符串
     * @returns {String} 格式化时间
     */
    formatTime(time)
    {
      if (!time)
      {
        return ''
      }
      return String(time).replace('T', ' ').slice(0, 16)
    },

    /**
     * 拉取阅读历史
     * @returns {Promise} 请求 Promise
     */
    loadHistory()
    {
      this.loading = true
      return getHistory()
        .then((res) =>
        {
          if (res.code === 200)
          {
            this.historyList = res.data
          }
          else
          {
            uni.showToast({ title: '请先登录', icon: 'none' })
          }
        })
        .catch(() => uni.showToast({ title: '加载失败', icon: 'none' }))
        .finally(() =>
        {
          this.loading = false
        })
    },
  },
}
</script>
