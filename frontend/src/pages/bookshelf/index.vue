<style lang="scss" scoped>
.bookshelf-page { display: flex; flex-direction: column; min-height: 100vh; background: #F8F6F1; }
.shelf-list { display: flex; flex-direction: column; padding: 24rpx; gap: 20rpx; }
.shelf-card { display: flex; padding: 24rpx; background: #FFFFFF; border-radius: 16rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06); }
.shelf-cover { display: flex; align-items: center; justify-content: center; width: 120rpx; height: 160rpx; margin-right: 24rpx; background: #EFE6D8; font-size: 36rpx; color: #8B5E3C; font-weight: 600; border-radius: 12rpx; }
.shelf-info { display: flex; flex: 1; flex-direction: column; justify-content: center; }
.shelf-name { font-size: 32rpx; color: #333333; font-weight: 600; }
.shelf-meta { font-size: 26rpx; color: #999999; margin-top: 10rpx; }
.shelf-progress { display: flex; align-items: center; margin-top: 16rpx; gap: 12rpx; }
.progress-label { font-size: 22rpx; color: #8B5E3C; background: #F5EFE6; padding: 4rpx 14rpx; border-radius: 8rpx; }
.shelf-remove { display: flex; align-items: center; justify-content: center; width: 88rpx; margin-left: 16rpx; font-size: 26rpx; color: #C0392B; }
.empty-tip { display: flex; align-items: center; justify-content: center; height: 400rpx; font-size: 28rpx; color: #999999; }
</style>
<template>
  <!-- 🚀 页面主体 -->
  <view class="bookshelf-page">
    <!-- 🚀 书架列表 -->
    <view class="shelf-list">
      <view v-for="item in shelfList" :key="item.shelfId" class="shelf-card" @click="handleOpenReader(item)">
        <view class="shelf-cover">{{ getCoverText(item) }}</view>
        <view class="shelf-info">
          <view class="shelf-name">{{ item.bookName }}</view>
          <view class="shelf-meta">{{ item.author }} · {{ item.dynasty }}</view>
          <view class="shelf-progress">
            <view class="progress-label">{{ getProgressText(item) }}</view>
          </view>
        </view>
        <view class="shelf-remove" @click.stop="handleRemove(item)">移出</view>
      </view>
      <view v-if="shelfList.length === 0 && !loading" class="empty-tip">书架空空如也，去首页挑一本吧</view>
    </view>
  </view>
</template>
<script>
/**
 * 组件名称：bookshelf
 * 功能说明：我的书架页面，展示收藏古籍及最近阅读进度，支持移出书架与继续阅读
 * 研发时间：2026/10/31
 * 研发人员：Doubao
 *
 * 变量说明：
 * @data {Array}   shelfList    - 书架条目列表
 * @data {Boolean} loading      - 是否加载中
 *
 * 事件说明：
 * @event onShow            - 页面显示时拉取书架数据
 * @event onPullDownRefresh - 下拉刷新书架
 * @event handleOpenReader  - 打开阅读器继续阅读
 * @event handleRemove      - 移出书架
 * @event getCoverText      - 获取封面占位文字
 * @event getProgressText   - 获取阅读进度文案
 * @event loadShelf         - 拉取书架列表
 *
 * 插槽说明：
 */
/**
 * 修改时间       人员        说明
 */

import { getBookshelf, deleteBookshelf } from '../../utils/gujiApi'

export default
{
  data()
  {
    return {
      shelfList: [],
      loading: false,
    }
  },

  onShow()
  {
    /**
     * 页面显示时拉取书架数据
     */
    this.loadShelf()
  },

  onPullDownRefresh()
  {
    /**
     * 下拉刷新书架
     */
    this.loadShelf().finally(() => uni.stopPullDownRefresh())
  },

  methods:
  {
    /**
     * 打开阅读器继续阅读
     * @param {Object} item - 书架条目
     */
    handleOpenReader(item)
    {
      if (item.lastChapterId)
      {
        uni.navigateTo({
          url: `/pages/reader/index?bookId=${item.bookId}&chapterId=${item.lastChapterId}&paragraphId=${item.lastParagraphId || 0}`,
        })
      }
      else
      {
        uni.navigateTo({ url: `/pages/book/detail?bookId=${item.bookId}` })
      }
    },

    /**
     * 移出书架
     * @param {Object} item - 书架条目
     */
    handleRemove(item)
    {
      uni.showModal({
        title: '提示',
        content: `确定将《${item.bookName}》移出书架吗？`,
        success: (res) =>
        {
          if (res.confirm)
          {
            deleteBookshelf(item.bookId)
              .then((res2) =>
              {
                if (res2.code === 200)
                {
                  uni.showToast({ title: '已移出', icon: 'success' })
                  this.loadShelf()
                }
              })
              .catch(() => uni.showToast({ title: '操作失败', icon: 'none' }))
          }
        },
      })
    },

    /**
     * 获取封面占位文字
     * @param {Object} item - 书架条目
     * @returns {String} 封面占位文字
     */
    getCoverText(item)
    {
      return item.bookName ? item.bookName.charAt(0) : '古'
    },

    /**
     * 获取阅读进度文案
     * @param {Object} item - 书架条目
     * @returns {String} 进度文案
     */
    getProgressText(item)
    {
      return item.lastChapterName ? `读到：${item.lastChapterName}` : '尚未开始阅读'
    },

    /**
     * 拉取书架列表
     * @returns {Promise} 请求 Promise
     */
    loadShelf()
    {
      this.loading = true
      return getBookshelf()
        .then((res) =>
        {
          if (res.code === 200)
          {
            this.shelfList = res.data
          }
          else if (res.code === 401 || res.code === 601)
          {
            uni.showToast({ title: '请先登录', icon: 'none' })
            setTimeout(() => uni.navigateTo({ url: '/pages/login/index' }), 600)
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
