<style lang="scss" scoped>
.page { display: flex; flex-direction: column; min-height: 100vh; background: #fbf7f0; }
.nav { display: flex; align-items: center; justify-content: space-between; padding: 24rpx 30rpx; background: #8c5a3c; }
.nav-title { font-size: 34rpx; color: #fff; font-weight: 600; }
.nav-action { font-size: 26rpx; color: #f0e2d0; }
.shelf-list { flex: 1; padding: 20rpx 30rpx; }
.shelf-item { display: flex; padding: 24rpx; margin-bottom: 20rpx; background: #ffffff; border-radius: 16rpx; }
.shelf-cover { width: 120rpx; height: 170rpx; border-radius: 10rpx; background: #e8dcc8; }
.shelf-info { flex: 1; display: flex; flex-direction: column; justify-content: space-between; margin-left: 24rpx; }
.shelf-name { font-size: 30rpx; color: #3a2c20; font-weight: 500; }
.shelf-author { margin-top: 8rpx; font-size: 24rpx; color: #9a8b7a; }
.shelf-progress { margin-top: 8rpx; font-size: 22rpx; color: #a0714b; }
.shelf-time { margin-top: 8rpx; font-size: 22rpx; color: #b0a79c; }
.shelf-remove { align-self: center; font-size: 24rpx; color: #c07070; padding: 8rpx 16rpx; }
.history-list { padding: 0 30rpx 30rpx; }
.history-item { display: flex; align-items: center; padding: 20rpx 0; border-bottom: 1rpx solid #efe6d8; }
.history-name { flex: 1; font-size: 28rpx; color: #3a2c20; }
.history-chapter { font-size: 22rpx; color: #9a8b7a; }
.empty { padding: 100rpx; text-align: center; font-size: 26rpx; color: #9a8b7a; }
</style>
<template>
  <view class="page">
    <view class="nav">
      <text class="nav-title">书架</text>
      <text class="nav-action" @click="onManage">{{ managing ? '完成' : '管理' }}</text>
    </view>

    <scroll-view class="shelf-list" scroll-y>
      <view
        class="shelf-item"
        v-for="item in shelfList"
        :key="item.shelfId"
        @click="onOpenBook(item)"
      >
        <image class="shelf-cover" :src="(item.bookInfo && item.bookInfo.coverUrl) || defaultCover" mode="aspectFill" />
        <view class="shelf-info">
          <text class="shelf-name">{{ (item.bookInfo && item.bookInfo.bookName) || ('书籍' + item.bizId) }}</text>
          <text class="shelf-author">{{ item.bookInfo ? item.bookInfo.authors : '' }}</text>
          <text class="shelf-progress">阅读进度：{{ item.progress || '0%' }}</text>
          <text class="shelf-time">最近阅读：{{ item.lastReadTime || '—' }}</text>
        </view>
        <text class="shelf-remove" v-if="managing" @click.stop="onRemove(item)">移出</text>
      </view>

      <view class="empty" v-if="!shelfList.length">书架还空着，去首页挑一本古籍吧</view>
    </scroll-view>

    <view class="section-head-simple" v-if="historyList.length">
      <text class="nav-title" style="padding: 20rpx 30rpx; color:#3a2c20;">最近阅读</text>
    </view>
    <view class="history-list">
      <view class="history-item" v-for="item in historyList" :key="item.historyId" @click="onOpenHistory(item)">
        <text class="history-name">{{ item.chapterName || ('书籍' + item.bizId) }}</text>
        <text class="history-chapter">{{ item.progress || '' }}</text>
      </view>
    </view>
  </view>
</template>
<script>
import { listShelf, deleteShelf, listHistory } from '@/api/guji.js'

/**
 * 识典古籍 - 书架
 * 对应原App Lynx shelf 页面：书架列表 + 最近阅读
 */
export default
{
  data()
  {
    return {
      shelfList: [],
      historyList: [],
      managing: false,
      defaultCover: '/static/logo.png'
    }
  },

  onShow()
  {
    this.loadData()
  },

  methods:
  {
    /**
     * 加载书架与历史
     */
    async loadData()
    {
      try
      {
        const [shelfRes, historyRes] = await Promise.all([
          listShelf({ pageNum: 1, pageSize: 50, shelfBizType: 'book' }),
          listHistory(1, 10)
        ])
        this.shelfList = shelfRes.shelfItemList || shelfRes.rows || []
        this.historyList = (historyRes.rows || []).slice(0, 5)
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '加载失败', icon: 'none' })
      }
    },

    /**
     * 切换管理模式
     */
    onManage()
    {
      this.managing = !this.managing
    },

    /**
     * 打开书籍
     * @param {Object} item 书架条目
     */
    onOpenBook(item)
    {
      uni.navigateTo({ url: `/pages/guji/book/book?bookId=${item.bizId}` })
    },

    /**
     * 打开历史记录对应书籍
     * @param {Object} item 历史条目
     */
    onOpenHistory(item)
    {
      uni.navigateTo({ url: `/pages/guji/book/book?bookId=${item.bizId}` })
    },

    /**
     * 移出书架
     * @param {Object} item 书架条目
     */
    async onRemove(item)
    {
      try
      {
        await deleteShelf([item.bizId])
        uni.showToast({ title: '已移出书架', icon: 'none' })
        this.loadData()
      }
      catch (err)
      {
        uni.showToast({ title: err.message || '操作失败', icon: 'none' })
      }
    }
  }
}
</script>
